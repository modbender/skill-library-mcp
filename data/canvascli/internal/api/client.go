package api

import (
	"bufio"
	"crypto/aes"
	"crypto/cipher"
	"crypto/hmac"
	cryptorand "crypto/rand"
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/http/cookiejar"
	"net/url"
	"os"
	"regexp"
	"strings"
	"time"

	"canvas-cli/internal/config"
)

var cryptoRandReader = io.Reader(cryptorand.Reader)

type Client struct {
	BaseURL    string
	SiteURL    string
	Config     *config.Config
	HTTPClient *http.Client
	PerPage    int
	loggedIn   bool
	retrying   bool
	Debug      bool
}

func NewClient(cfg *config.Config) *Client {
	jar, _ := cookiejar.New(nil)
	return &Client{
		SiteURL: strings.TrimRight(cfg.APIURL, "/"),
		BaseURL: strings.TrimRight(cfg.APIURL, "/") + "/api/v1",
		Config:  cfg,
		HTTPClient: &http.Client{
			Timeout: 60 * time.Second,
			Jar:     jar,
		},
		PerPage: 50,
	}
}

func (c *Client) debugf(format string, args ...interface{}) {
	if c.Debug {
		fmt.Printf("  [debug] "+format+"\n", args...)
	}
}

// Login performs the full SAML SSO login flow for Tec de Monterrey:
// 1. GET Canvas /login → 302 to /login/saml → 302 to amfs.tec.mx with SAMLRequest
// 2. GET amfs.tec.mx SAML SSO page → returns page with form action to credential endpoint
// 3. POST credentials to the credential form action URL
// 4. Response contains SAMLResponse form → POST back to Canvas
// 5. Canvas establishes session
func (c *Client) Login() error {
	if c.loggedIn {
		return nil
	}

	// Try restoring saved session cookies first
	if len(c.Config.Cookies) > 0 && !c.Debug {
		if c.tryRestoredSession() {
			return nil
		}
	}

	if !c.Debug {
		fmt.Print("  Logging in... ")
	}

	noRedir := c.noRedirectClient()

	// Step 1: GET Canvas /login → auto-follow all redirects to amfs.tec.mx IdP login form
	// We use the main HTTP client (with auto-redirect) to preserve all cookies from the chain.
	// Then we use the body from the FINAL 200 response directly — no separate GET.
	c.debugf("Step 1: GET %s/login → follow all redirects to IdP", c.SiteURL)

	startReq, _ := http.NewRequest("GET", c.SiteURL+"/login", nil)
	startReq.Header.Set("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 canvas-cli/1.0")
	startReq.Header.Set("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")

	resp, err := c.HTTPClient.Do(startReq)
	if err != nil {
		c.loginFailed()
		return fmt.Errorf("reaching IdP: %w", err)
	}
	idpBody, _ := io.ReadAll(resp.Body)
	resp.Body.Close()

	idpPageBody := string(idpBody)
	idpPageURL := resp.Request.URL.String()

	c.debugf("  → Final URL: %s", idpPageURL)
	c.debugf("  → Status: %d, Body: %d bytes", resp.StatusCode, len(idpBody))

	if resp.StatusCode != 200 || idpPageBody == "" {
		c.loginFailed()
		return fmt.Errorf("could not reach login form (status %d)", resp.StatusCode)
	}

	if c.Debug {
		os.WriteFile("/tmp/canvas_step1.html", []byte(idpPageBody), 0644)
		c.debugf("  → Saved initial page to /tmp/canvas_step1.html (%d bytes)", len(idpPageBody))
	}

	// The IdP may return an intermediate auto-submit form page (JavaScript does document.forms[0].submit()).
	// We need to detect this and perform the POST to get the actual login form.
	if strings.Contains(idpPageBody, "document.forms[0].submit()") || (len(idpPageBody) < 1000 && strings.Contains(idpPageBody, "<form") && !strings.Contains(idpPageBody, "Ecom_User_ID")) {
		autoAction := extractFormAction2(idpPageBody, idpPageURL)
		if autoAction == "" {
			autoAction = idpPageURL
		}
		autoFields := extractAllHiddenFields(idpPageBody)
		c.debugf("  → Auto-submit form detected → POST to %s", autoAction)

		autoReq, _ := http.NewRequest("POST", autoAction, strings.NewReader(autoFields.Encode()))
		autoReq.Header.Set("Content-Type", "application/x-www-form-urlencoded")
		autoReq.Header.Set("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
		autoReq.Header.Set("Referer", idpPageURL)
		autoReq.Header.Set("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 canvas-cli/1.0")

		autoResp, err := c.HTTPClient.Do(autoReq)
		if err != nil {
			c.loginFailed()
			return fmt.Errorf("submitting auto-form: %w", err)
		}
		autoBody, _ := io.ReadAll(autoResp.Body)
		autoResp.Body.Close()

		idpPageBody = string(autoBody)
		idpPageURL = autoResp.Request.URL.String()

		c.debugf("  → Login form URL: %s", idpPageURL)
		c.debugf("  → Login form size: %d bytes", len(idpPageBody))

		if c.Debug {
			os.WriteFile("/tmp/canvas_step1b.html", autoBody, 0644)
			c.debugf("  → Saved login form to /tmp/canvas_step1b.html")
		}
	}

	// Debug: show cookies
	if c.Debug {
		postURL, _ := url.Parse(idpPageURL)
		if postURL != nil {
			cookies := c.HTTPClient.Jar.Cookies(postURL)
			c.debugf("  → Cookies for %s: %d", postURL.Host, len(cookies))
			for _, cookie := range cookies {
				val := cookie.Value
				if len(val) > 60 {
					val = val[:60] + "..."
				}
				c.debugf("    %s = %s", cookie.Name, val)
			}
		}
	}

	// Step 2: Extract form action and hidden fields from the login form
	c.debugf("Step 2: Extracting form data from login form")
	postAction := extractFormAction2(idpPageBody, idpPageURL)
	if postAction == "" {
		postAction = idpPageURL
	}
	c.debugf("  → POST action: %s", postAction)

	hiddenFields := extractAllHiddenFields(idpPageBody)
	c.debugf("  → Hidden fields: %v", hiddenFieldNames(hiddenFields))
	for k, v := range hiddenFields {
		val := v[0]
		if len(val) > 80 {
			val = val[:80] + "..."
		}
		c.debugf("    %s = %s", k, val)
	}

	// Step 3: POST credentials
	c.debugf("Step 3: POST credentials to %s", postAction)
	form := url.Values{}
	// Include any hidden fields from the form
	for k, v := range hiddenFields {
		form[k] = v
	}

	// Set credentials
	// The IdP expects Ecom_User_ID in "user@domain" format (validated by JS)
	// ddlDomain should remain empty as in the original form
	form.Set("Ecom_User_ID", c.Config.Username)
	form.Set("Ecom_Password", c.Config.Password)

	// The Tec de Monterrey IdP encodes the password as Base64 in the "itesm64" field
	// This is done by JavaScript in the browser before form submission
	encodedPassword := base64.StdEncoding.EncodeToString([]byte(c.Config.Password))
	form.Set("itesm64", encodedPassword)
	c.debugf("  → itesm64 (base64 password): set")

	req, _ := http.NewRequest("POST", postAction, strings.NewReader(form.Encode()))
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Set("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
	req.Header.Set("Referer", idpPageURL)
	req.Header.Set("Origin", extractOrigin(idpPageURL))
	req.Header.Set("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 canvas-cli/1.0")

	postResp, err := noRedir.Do(req)
	if err != nil {
		c.loginFailed()
		return fmt.Errorf("credential POST failed: %w", err)
	}
	postBody, _ := io.ReadAll(postResp.Body)
	postResp.Body.Close()
	postBodyStr := string(postBody)

	c.debugf("  → Status: %d, Body: %d bytes", postResp.StatusCode, len(postBody))
	c.debugf("  → Has SAMLResponse: %v", strings.Contains(postBodyStr, "SAMLResponse"))
	if c.Debug {
		os.WriteFile("/tmp/canvas_step3.html", postBody, 0644)
		c.debugf("  → Saved POST response to /tmp/canvas_step3.html")
	}

	// Show posted form values in debug
	c.debugf("  → Posted fields:")
	for k, v := range form {
		val := v[0]
		if k == "Ecom_Password" {
			val = "***"
		}
		if len(val) > 80 {
			val = val[:80] + "..."
		}
		c.debugf("    %s = %s", k, val)
	}

	// Check for error messages in response
	if c.Debug && !strings.Contains(postBodyStr, "SAMLResponse") {
		// Look for error divs/spans
		errorRe := regexp.MustCompile(`(?i)class="[^"]*error[^"]*"[^>]*>([^<]+)`)
		errorMatches := errorRe.FindAllStringSubmatch(postBodyStr, 5)
		for _, m := range errorMatches {
			c.debugf("  → Error element: %s", strings.TrimSpace(m[1]))
		}
		// Look for alert messages
		alertRe := regexp.MustCompile(`(?i)class="[^"]*alert[^"]*"[^>]*>([^<]+)`)
		alertMatches := alertRe.FindAllStringSubmatch(postBodyStr, 5)
		for _, m := range alertMatches {
			c.debugf("  → Alert element: %s", strings.TrimSpace(m[1]))
		}
		// Show a snippet around any "error" or "invalid" text
		lowerBody := strings.ToLower(postBodyStr)
		for _, keyword := range []string{"error", "invalid", "incorrecto", "failed", "denied"} {
			idx := strings.Index(lowerBody, keyword)
			if idx >= 0 {
				start := idx - 100
				if start < 0 {
					start = 0
				}
				end := idx + 200
				if end > len(postBodyStr) {
					end = len(postBodyStr)
				}
				c.debugf("  → Found '%s' near: ...%s...", keyword, strings.TrimSpace(postBodyStr[start:end]))
				break
			}
		}
	}

	// Step 4: Handle the response — may require device fingerprinting or contain SAMLResponse
	if postResp.StatusCode == 302 || postResp.StatusCode == 301 || postResp.StatusCode == 303 {
		location := postResp.Header.Get("Location")
		c.debugf("Step 4: Following redirect to %s", location)
		err = c.followChainAndHandleSAML(location, idpPageURL)
		if err != nil {
			c.loginFailed()
			return fmt.Errorf("following post-login redirects: %w", err)
		}
	} else {
		err = c.handlePostLoginResponse(postResp.StatusCode, postBodyStr, noRedir, idpPageURL)
		if err != nil {
			c.loginFailed()
			return err
		}
	}

	// Step 5: Verify API access
	c.debugf("Step 5: Verifying API access")
	testReq, _ := http.NewRequest("GET", c.BaseURL+"/users/self/profile", nil)
	testReq.Header.Set("Accept", "application/json")
	testResp, err := c.HTTPClient.Do(testReq)
	if err != nil {
		c.loginFailed()
		return fmt.Errorf("verifying login: %w", err)
	}
	testBody, _ := io.ReadAll(testResp.Body)
	testResp.Body.Close()

	c.debugf("  → API Status: %d", testResp.StatusCode)

	if testResp.StatusCode == 200 {
		var profile struct {
			Name string `json:"name"`
		}
		json.Unmarshal(testBody, &profile)
		if !c.Debug {
			if profile.Name != "" {
				fmt.Printf("OK (%s)\n", profile.Name)
			} else {
				fmt.Println("OK")
			}
		}
		c.loggedIn = true
		c.saveSessionCookies()
		return nil
	}

	c.loginFailed()
	return fmt.Errorf("login flow completed but API returned %d — session not established", testResp.StatusCode)
}

// handlePostLoginResponse processes the response after credential POST.
// It handles: SAMLResponse pages, device fingerprinting (recon) pages, redirects, or login form errors.
// The method may recurse since the recon step produces another response to handle.
func (c *Client) handlePostLoginResponse(statusCode int, bodyStr string, noRedir *http.Client, referer string) error {
	if statusCode == 200 {
		if strings.Contains(bodyStr, "SAMLResponse") {
			c.debugf("Step 4: Found SAMLResponse → submitting to Canvas")
			return c.submitSAMLResponse(bodyStr)
		}

		// Device fingerprinting / reconnaissance page
		if strings.Contains(bodyStr, "deviceRecon") || strings.Contains(bodyStr, "deviceAttributes") {
			c.debugf("Step 4: Device fingerprinting page detected")
			return c.handleDeviceRecon(bodyStr, noRedir, referer)
		}

		// TOTP / MFA page — user must provide a one-time code
		if strings.Contains(bodyStr, "nffc") || strings.Contains(bodyStr, "TOTP") || strings.Contains(bodyStr, "One-Time") || strings.Contains(bodyStr, "One Time Password") {
			c.debugf("  → MFA/TOTP page detected")
			return c.handleMFA(bodyStr, noRedir, referer)
		}

		// Login form returned again — bad credentials
		if strings.Contains(bodyStr, "Ecom_User_ID") || strings.Contains(bodyStr, "loginForm") {
			return fmt.Errorf("login failed — the IdP returned the login form again. Check username/password (run: canvas-cli configure)")
		}

		// Auto-submit form (JavaScript does document.forms[...].submit())
		if strings.Contains(bodyStr, ".submit()") && strings.Contains(bodyStr, "<form") {
			autoAction := extractFormAction2(bodyStr, referer)
			if autoAction != "" {
				c.debugf("  → Auto-submit form detected → POST to %s", autoAction)
				autoFields := extractAllHiddenFields(bodyStr)
				c.debugf("  → Auto-submit fields: %v", hiddenFieldNames(autoFields))

				autoReq, _ := http.NewRequest("POST", autoAction, strings.NewReader(autoFields.Encode()))
				autoReq.Header.Set("Content-Type", "application/x-www-form-urlencoded")
				autoReq.Header.Set("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
				autoReq.Header.Set("Referer", referer)
				autoReq.Header.Set("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 canvas-cli/1.0")

				autoResp, err := c.HTTPClient.Do(autoReq)
				if err != nil {
					return fmt.Errorf("auto-submit form POST failed: %w", err)
				}
				autoBody, _ := io.ReadAll(autoResp.Body)
				autoResp.Body.Close()
				autoBodyStr := string(autoBody)

				c.debugf("  → Auto-submit response: %d, %d bytes, final URL: %s", autoResp.StatusCode, len(autoBody), autoResp.Request.URL.String())
				if c.Debug {
					os.WriteFile("/tmp/canvas_autosubmit.html", autoBody, 0644)
				}

				// The auto-redirect client may have followed redirects; check final page
				if strings.Contains(autoBodyStr, "SAMLResponse") {
					return c.submitSAMLResponse(autoBodyStr)
				}
				// Recurse (with depth protection via the auto-submit check)
				return c.handlePostLoginResponse(autoResp.StatusCode, autoBodyStr, noRedir, autoResp.Request.URL.String())
			}
		}

		// JavaScript redirect: window.location.href='...'
		jsRedirectRe := regexp.MustCompile(`(?i)window\.location\.href\s*=\s*'([^']+)'`)
		if m := jsRedirectRe.FindStringSubmatch(bodyStr); len(m) >= 2 {
			jsURL := resolveURL(referer, m[1])
			c.debugf("  → JavaScript redirect detected → GET %s", jsURL)

			jsReq, _ := http.NewRequest("GET", jsURL, nil)
			jsReq.Header.Set("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
			jsReq.Header.Set("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 canvas-cli/1.0")

			jsResp, err := c.HTTPClient.Do(jsReq)
			if err != nil {
				return fmt.Errorf("JS redirect GET failed: %w", err)
			}
			jsBody, _ := io.ReadAll(jsResp.Body)
			jsResp.Body.Close()
			jsBodyStr := string(jsBody)
			jsFinalURL := jsResp.Request.URL.String()

			c.debugf("  → JS redirect response: %d, %d bytes, final URL: %s", jsResp.StatusCode, len(jsBody), jsFinalURL)
			c.debugf("  → Has SAMLResponse: %v", strings.Contains(jsBodyStr, "SAMLResponse"))
			if c.Debug {
				os.WriteFile("/tmp/canvas_jsredirect.html", jsBody, 0644)
			}

			if strings.Contains(jsBodyStr, "SAMLResponse") {
				return c.submitSAMLResponse(jsBodyStr)
			}
			return c.handlePostLoginResponse(jsResp.StatusCode, jsBodyStr, noRedir, jsFinalURL)
		}

		// Unknown 200 page
		if c.Debug {
			os.WriteFile("/tmp/canvas_unknown.html", []byte(bodyStr), 0644)
			c.debugf("  → Unknown page saved to /tmp/canvas_unknown.html (%d bytes)", len(bodyStr))
		}
		return fmt.Errorf("unexpected response after login POST (no SAMLResponse found, %d bytes)", len(bodyStr))
	}

	return fmt.Errorf("unexpected login response: HTTP %d", statusCode)
}

// handleDeviceRecon handles the NetIQ/NAM device fingerprinting (reconnaissance) page.
// The IdP requires a device fingerprint before completing the SAML flow.
// The fingerprint is signed+encrypted using JWE with keys embedded in the page.
// Since this requires complex crypto (node-jose), we generate a minimal fingerprint
// and submit it. If the server rejects it, we'll need a browser-assisted approach.
func (c *Client) handleDeviceRecon(bodyStr string, noRedir *http.Client, referer string) error {
	// Extract the form action
	actionURL := extractFormAction2(bodyStr, referer)
	if actionURL == "" {
		return fmt.Errorf("no form action in device recon page")
	}
	c.debugf("  → Recon form action: %s", actionURL)

	// Extract hidden fields
	reconFields := extractAllHiddenFields(bodyStr)

	// Extract the signing and encryption keys from the inline JavaScript
	sigKeyRe := regexp.MustCompile(`"use":"sig"[^}]*"k":"([^"]+)"`)
	encKeyRe := regexp.MustCompile(`"use":"enc"[^}]*"k":"([^"]+)"`)

	sigKeyMatch := sigKeyRe.FindStringSubmatch(bodyStr)
	encKeyMatch := encKeyRe.FindStringSubmatch(bodyStr)

	var sigKeyB64, encKeyB64 string
	if len(sigKeyMatch) >= 2 {
		sigKeyB64 = sigKeyMatch[1]
	}
	if len(encKeyMatch) >= 2 {
		encKeyB64 = encKeyMatch[1]
	}
	c.debugf("  → Signing key: %s", sigKeyB64)
	c.debugf("  → Encryption key: %s", encKeyB64)

	// Build a plausible device fingerprint JSON.
	// The IdP's getFingerprint() collects browser attributes and returns a JSON string.
	// We construct one that matches what a real browser would send.
	fingerprint := fmt.Sprintf(`{"deviceType":"Desktop","screenResolution_availableScreenResolution":"1440x900","deviceLanguage_deviceDefaultLanguage":"en-US","screenResolution_screenResolution":"1440x900","accept-language":"en-US,en;q=0.9,es;q=0.8","userAgent_uaVersion":"537.36","cpuArchitecture_cpuArchitecture":"amd64","dnt":"unspecified","operatingSystem_osVersion":"10.15.7","accept-charset":"utf-8","deviceLanguage_deviceLanguageSet":"en-US,en,es","userAgent_uaName":"Chrome","navigatorConcurrency":"8","deviceTouchSupport":"false","timezoneOffset":"-360","deviceTouchPoints":"0","navigatorPlatform_navigatorPlatform":"MacIntel","colorDepth":"24","operatingSystem_osName":"Mac OS","accept-encoding":"gzip, deflate, br","userDN":"","user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36","userAgent_uaString":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}`)

	// The server expects the fingerprint to be signed (JWS) then encrypted (JWE).
	// We need to produce a JWE compact serialization.
	// If we have valid keys, try to do the crypto. Otherwise submit raw.
	var deviceAttrValue string
	if sigKeyB64 != "" && encKeyB64 != "" {
		signed, err := c.jwsSign(fingerprint, sigKeyB64)
		if err != nil {
			c.debugf("  → JWS signing failed: %v, submitting raw fingerprint", err)
			deviceAttrValue = fingerprint
		} else {
			encrypted, err := c.jweEncrypt(signed, encKeyB64)
			if err != nil {
				c.debugf("  → JWE encryption failed: %v, submitting signed fingerprint", err)
				deviceAttrValue = signed
			} else {
				deviceAttrValue = encrypted
				c.debugf("  → Fingerprint signed+encrypted successfully")
			}
		}
	} else {
		c.debugf("  → No crypto keys found, submitting raw fingerprint")
		deviceAttrValue = fingerprint
	}

	reconFields.Set("deviceAttributes", deviceAttrValue)
	c.debugf("  → Submitting recon form to %s", actionURL)

	req, _ := http.NewRequest("POST", actionURL, strings.NewReader(reconFields.Encode()))
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Set("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
	req.Header.Set("Referer", referer)
	req.Header.Set("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

	resp, err := noRedir.Do(req)
	if err != nil {
		return fmt.Errorf("recon POST failed: %w", err)
	}
	reconRespBody, _ := io.ReadAll(resp.Body)
	resp.Body.Close()
	reconRespStr := string(reconRespBody)

	c.debugf("  → Recon response: %d, %d bytes", resp.StatusCode, len(reconRespBody))
	c.debugf("  → Has SAMLResponse: %v", strings.Contains(reconRespStr, "SAMLResponse"))

	if c.Debug {
		os.WriteFile("/tmp/canvas_step4_recon.html", reconRespBody, 0644)
		c.debugf("  → Saved recon response to /tmp/canvas_step4_recon.html")
	}

	// Handle redirect after recon
	if resp.StatusCode == 302 || resp.StatusCode == 301 || resp.StatusCode == 303 {
		location := resp.Header.Get("Location")
		c.debugf("  → Recon redirect to: %s", location)
		return c.followChainAndHandleSAML(location, referer)
	}

	// Recurse to handle the next page (could be SAMLResponse, another form, etc.)
	return c.handlePostLoginResponse(resp.StatusCode, reconRespStr, noRedir, referer)
}

// jwsSign creates a JWS compact serialization (HS256) of the payload
func (c *Client) jwsSign(payload string, keyB64 string) (string, error) {
	keyBytes, err := base64.StdEncoding.DecodeString(keyB64)
	if err != nil {
		// Try URL-safe base64
		keyBytes, err = base64.URLEncoding.DecodeString(keyB64)
		if err != nil {
			return "", fmt.Errorf("decode signing key: %w", err)
		}
	}

	// JWS header: {"alg":"HS256"}
	header := base64URLEncode([]byte(`{"alg":"HS256"}`))
	payloadB64 := base64URLEncode([]byte(payload))
	signingInput := header + "." + payloadB64

	// HMAC-SHA256
	mac := hmacSHA256([]byte(signingInput), keyBytes)
	signature := base64URLEncode(mac)

	return signingInput + "." + signature, nil
}

// jweEncrypt creates a JWE compact serialization (A128CBC-HS256, dir key agreement) of the payload
func (c *Client) jweEncrypt(payload string, keyB64 string) (string, error) {
	keyBytes, err := base64.StdEncoding.DecodeString(keyB64)
	if err != nil {
		keyBytes, err = base64.URLEncoding.DecodeString(keyB64)
		if err != nil {
			return "", fmt.Errorf("decode encryption key: %w", err)
		}
	}

	// A128CBC-HS256 uses a 32-byte key: first 16 for HMAC, last 16 for AES
	if len(keyBytes) < 32 {
		return "", fmt.Errorf("encryption key too short: %d bytes (need 32)", len(keyBytes))
	}

	macKey := keyBytes[:16]
	encKey := keyBytes[16:32]

	// JWE header: {"alg":"dir","enc":"A128CBC-HS256"}
	headerJSON := `{"alg":"dir","enc":"A128CBC-HS256"}`
	headerB64 := base64URLEncode([]byte(headerJSON))

	// No wrapped key for "dir" algorithm
	encryptedKeyB64 := ""

	// Generate random IV (16 bytes for AES-CBC)
	iv := make([]byte, 16)
	if _, err := io.ReadFull(cryptoRandReader, iv); err != nil {
		return "", fmt.Errorf("generating IV: %w", err)
	}
	ivB64 := base64URLEncode(iv)

	// Pad plaintext with PKCS7
	plaintext := []byte(payload)
	padLen := 16 - (len(plaintext) % 16)
	for i := 0; i < padLen; i++ {
		plaintext = append(plaintext, byte(padLen))
	}

	// AES-128-CBC encrypt
	block, err := aes.NewCipher(encKey)
	if err != nil {
		return "", fmt.Errorf("AES cipher: %w", err)
	}
	ciphertext := make([]byte, len(plaintext))
	mode := cipher.NewCBCEncrypter(block, iv)
	mode.CryptBlocks(ciphertext, plaintext)
	ciphertextB64 := base64URLEncode(ciphertext)

	// Compute authentication tag: HMAC-SHA256 over AAD || IV || ciphertext || AL
	// AAD = header bytes (ASCII), AL = big-endian 64-bit bit length of AAD
	aad := []byte(headerB64)
	al := make([]byte, 8)
	aadBitLen := uint64(len(aad) * 8)
	al[0] = byte(aadBitLen >> 56)
	al[1] = byte(aadBitLen >> 48)
	al[2] = byte(aadBitLen >> 40)
	al[3] = byte(aadBitLen >> 32)
	al[4] = byte(aadBitLen >> 24)
	al[5] = byte(aadBitLen >> 16)
	al[6] = byte(aadBitLen >> 8)
	al[7] = byte(aadBitLen)

	var authInput []byte
	authInput = append(authInput, aad...)
	authInput = append(authInput, iv...)
	authInput = append(authInput, ciphertext...)
	authInput = append(authInput, al...)

	fullTag := hmacSHA256(authInput, macKey)
	// Truncate to first 16 bytes for A128CBC-HS256
	tag := fullTag[:16]
	tagB64 := base64URLEncode(tag)

	// JWE compact: header.encryptedKey.iv.ciphertext.tag
	return headerB64 + "." + encryptedKeyB64 + "." + ivB64 + "." + ciphertextB64 + "." + tagB64, nil
}

// handleMFA handles the TOTP/MFA page by prompting the user for their one-time code.
func (c *Client) handleMFA(bodyStr string, noRedir *http.Client, referer string) error {
	// Extract form action
	actionURL := extractFormAction2(bodyStr, referer)
	if actionURL == "" {
		return fmt.Errorf("no form action in MFA page")
	}
	c.debugf("  → MFA form action: %s", actionURL)

	// Extract all hidden fields
	mfaFields := extractAllHiddenFields(bodyStr)
	c.debugf("  → MFA hidden fields: %v", hiddenFieldNames(mfaFields))

	// Prompt user for TOTP code
	fmt.Println()
	fmt.Print("  Enter your TOTP code: ")
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Scan()
	totpCode := strings.TrimSpace(scanner.Text())

	if totpCode == "" {
		return fmt.Errorf("no TOTP code provided")
	}

	// Set the OTP field
	mfaFields.Set("nffc", totpCode)
	c.debugf("  → Submitting TOTP code to %s", actionURL)

	req, _ := http.NewRequest("POST", actionURL, strings.NewReader(mfaFields.Encode()))
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Set("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
	req.Header.Set("Referer", referer)
	req.Header.Set("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 canvas-cli/1.0")

	// Use auto-redirect client to follow the full chain after MFA
	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return fmt.Errorf("MFA POST failed: %w", err)
	}
	mfaRespBody, _ := io.ReadAll(resp.Body)
	resp.Body.Close()
	mfaRespStr := string(mfaRespBody)
	finalURL := resp.Request.URL.String()

	c.debugf("  → MFA response: %d, %d bytes, final URL: %s", resp.StatusCode, len(mfaRespBody), finalURL)
	c.debugf("  → Has SAMLResponse: %v", strings.Contains(mfaRespStr, "SAMLResponse"))

	if c.Debug {
		os.WriteFile("/tmp/canvas_step_mfa.html", mfaRespBody, 0644)
		c.debugf("  → Saved MFA response to /tmp/canvas_step_mfa.html")
	}

	// Check if auto-redirect already landed on Canvas (session established)
	if strings.Contains(finalURL, c.SiteURL) || strings.Contains(finalURL, "experiencia21") {
		c.debugf("  → Redirected back to Canvas — session should be established")
		return nil
	}

	// If the response contains SAMLResponse, submit it
	if strings.Contains(mfaRespStr, "SAMLResponse") {
		c.debugf("  → Found SAMLResponse after MFA")
		return c.submitSAMLResponse(mfaRespStr)
	}

	// Handle auto-submit forms or other intermediate pages
	return c.handlePostLoginResponse(resp.StatusCode, mfaRespStr, noRedir, finalURL)
}

// submitSAMLResponse extracts SAMLResponse from HTML and POSTs it to the SP (Canvas)
func (c *Client) submitSAMLResponse(bodyStr string) error {
	// Extract form action
	actionRe := regexp.MustCompile(`(?i)<form[^>]*action="([^"]+)"`)
	actionMatches := actionRe.FindStringSubmatch(bodyStr)
	if len(actionMatches) < 2 {
		return fmt.Errorf("no form action in SAML response page")
	}
	actionURL := strings.ReplaceAll(actionMatches[1], "&amp;", "&")
	c.debugf("  → SAML POST to: %s", actionURL)

	// Extract all hidden fields (SAMLResponse, RelayState, etc)
	form := extractAllHiddenFields(bodyStr)
	c.debugf("  → SAML fields: %v", hiddenFieldNames(form))

	if form.Get("SAMLResponse") == "" {
		return fmt.Errorf("SAMLResponse field is empty")
	}

	// POST to Canvas SAML consumer
	req, _ := http.NewRequest("POST", actionURL, strings.NewReader(form.Encode()))
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Set("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
	req.Header.Set("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 canvas-cli/1.0")

	// Use main client to follow all redirects and collect session cookies
	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return fmt.Errorf("SAML response POST: %w", err)
	}
	io.ReadAll(resp.Body)
	resp.Body.Close()

	c.debugf("  → SAML response POST result: %d, final URL: %s", resp.StatusCode, resp.Request.URL.String())

	return nil
}

// followChainAndHandleSAML follows redirects and handles any SAML forms encountered
func (c *Client) followChainAndHandleSAML(startURL string, referer string) error {
	noRedir := c.noRedirectClient()
	currentURL := startURL

	for i := 0; i < 15; i++ {
		if !strings.HasPrefix(currentURL, "http") {
			currentURL = resolveURL(referer, currentURL)
		}

		req, _ := http.NewRequest("GET", currentURL, nil)
		req.Header.Set("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 canvas-cli/1.0")
		req.Header.Set("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")

		resp, err := noRedir.Do(req)
		if err != nil {
			return err
		}
		body, _ := io.ReadAll(resp.Body)
		resp.Body.Close()

		if resp.StatusCode == 302 || resp.StatusCode == 301 || resp.StatusCode == 303 {
			currentURL = resp.Header.Get("Location")
			continue
		}

		if resp.StatusCode == 200 {
			bodyStr := string(body)
			if strings.Contains(bodyStr, "SAMLResponse") {
				return c.submitSAMLResponse(bodyStr)
			}
			return nil
		}

		return fmt.Errorf("unexpected status %d during redirect", resp.StatusCode)
	}
	return fmt.Errorf("too many redirects")
}

func (c *Client) noRedirectClient() *http.Client {
	return &http.Client{
		Jar:     c.HTTPClient.Jar,
		Timeout: 60 * time.Second,
		CheckRedirect: func(req *http.Request, via []*http.Request) error {
			return http.ErrUseLastResponse
		},
	}
}

func (c *Client) loginFailed() {
	if !c.Debug {
		fmt.Println("failed")
	}
}

// tryRestoredSession loads saved cookies into the jar and tests if the session is still valid.
func (c *Client) tryRestoredSession() bool {
	siteURL, _ := url.Parse(c.SiteURL)
	if siteURL == nil {
		return false
	}

	// Build http.Cookie list from saved cookies
	var cookies []*http.Cookie
	for _, sc := range c.Config.Cookies {
		cookies = append(cookies, &http.Cookie{
			Name:   sc.Name,
			Value:  sc.Value,
			Domain: sc.Domain,
			Path:   sc.Path,
		})
	}
	c.HTTPClient.Jar.SetCookies(siteURL, cookies)

	// Quick test: GET /api/v1/users/self/profile
	testReq, _ := http.NewRequest("GET", c.BaseURL+"/users/self/profile", nil)
	testReq.Header.Set("Accept", "application/json")
	testResp, err := c.HTTPClient.Do(testReq)
	if err != nil {
		return false
	}
	testBody, _ := io.ReadAll(testResp.Body)
	testResp.Body.Close()

	if testResp.StatusCode == 200 {
		var profile struct {
			Name string `json:"name"`
		}
		json.Unmarshal(testBody, &profile)
		if profile.Name != "" {
			fmt.Printf("  Session restored (%s)\n", profile.Name)
		}
		c.loggedIn = true
		return true
	}
	return false
}

// saveSessionCookies persists the current cookie jar to config for reuse.
func (c *Client) saveSessionCookies() {
	siteURL, _ := url.Parse(c.SiteURL)
	if siteURL == nil {
		return
	}

	cookies := c.HTTPClient.Jar.Cookies(siteURL)
	var saved []config.SavedCookie
	for _, cookie := range cookies {
		saved = append(saved, config.SavedCookie{
			Name:   cookie.Name,
			Value:  cookie.Value,
			Domain: cookie.Domain,
			Path:   cookie.Path,
		})
	}

	c.Config.Cookies = saved
	config.Save(c.Config)
}

func (c *Client) ensureLoggedIn() error {
	if c.loggedIn {
		return nil
	}
	return c.Login()
}

func (c *Client) request(method, endpoint string, body io.Reader, contentType string) ([]byte, error) {
	if err := c.ensureLoggedIn(); err != nil {
		return nil, err
	}

	u := c.BaseURL + endpoint
	if !strings.Contains(u, "per_page=") {
		sep := "?"
		if strings.Contains(u, "?") {
			sep = "&"
		}
		u += fmt.Sprintf("%sper_page=%d", sep, c.PerPage)
	}

	req, err := http.NewRequest(method, u, body)
	if err != nil {
		return nil, fmt.Errorf("creating request: %w", err)
	}

	req.Header.Set("Accept", "application/json")
	if contentType != "" {
		req.Header.Set("Content-Type", contentType)
	}

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	data, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("reading response: %w", err)
	}

	if resp.StatusCode == 401 && !c.retrying {
		c.loggedIn = false
		c.retrying = true
		if err := c.Login(); err != nil {
			c.retrying = false
			return nil, fmt.Errorf("session expired and re-login failed: %w", err)
		}
		result, err := c.request(method, endpoint, body, contentType)
		c.retrying = false
		return result, err
	}

	if resp.StatusCode == 403 {
		return nil, fmt.Errorf("forbidden — you don't have permission for this action")
	}
	if resp.StatusCode == 404 {
		return nil, fmt.Errorf("not found — check the ID and try again")
	}
	if resp.StatusCode >= 400 {
		return nil, fmt.Errorf("API error %d: %s", resp.StatusCode, string(data))
	}

	return data, nil
}

func (c *Client) GET(endpoint string) ([]byte, error) {
	return c.request("GET", endpoint, nil, "")
}

func (c *Client) POST(endpoint string, form url.Values) ([]byte, error) {
	return c.request("POST", endpoint, strings.NewReader(form.Encode()), "application/x-www-form-urlencoded")
}

func (c *Client) PUT(endpoint string, form url.Values) ([]byte, error) {
	return c.request("PUT", endpoint, strings.NewReader(form.Encode()), "application/x-www-form-urlencoded")
}

func (c *Client) DELETE(endpoint string) ([]byte, error) {
	return c.request("DELETE", endpoint, nil, "")
}

func (c *Client) GetJSON(endpoint string, target interface{}) error {
	data, err := c.GET(endpoint)
	if err != nil {
		return err
	}
	return json.Unmarshal(data, target)
}

func (c *Client) GetPaginated(endpoint string) ([]json.RawMessage, error) {
	var all []json.RawMessage
	page := 1
	for {
		sep := "?"
		if strings.Contains(endpoint, "?") {
			sep = "&"
		}
		pageURL := fmt.Sprintf("%s%spage=%d", endpoint, sep, page)
		data, err := c.GET(pageURL)
		if err != nil {
			return nil, err
		}
		var items []json.RawMessage
		if err := json.Unmarshal(data, &items); err != nil {
			return nil, err
		}
		if len(items) == 0 {
			break
		}
		all = append(all, items...)
		if len(items) < c.PerPage {
			break
		}
		page++
	}
	return all, nil
}

// --- Helper functions ---

// extractFormAction2 extracts form action URL from HTML body
func extractFormAction2(bodyStr, pageURL string) string {
	// Try loginForm specifically
	re1 := regexp.MustCompile(`(?i)<form[^>]*id\s*=\s*"loginForm"[^>]*action\s*=\s*"([^"]+)"`)
	if m := re1.FindStringSubmatch(bodyStr); len(m) >= 2 {
		return resolveURL(pageURL, strings.ReplaceAll(m[1], "&amp;", "&"))
	}

	// Try any form with action
	re2 := regexp.MustCompile(`(?i)<form[^>]*action\s*=\s*"([^"]+)"`)
	if m := re2.FindStringSubmatch(bodyStr); len(m) >= 2 {
		return resolveURL(pageURL, strings.ReplaceAll(m[1], "&amp;", "&"))
	}

	return ""
}

// extractAllHiddenFields extracts all hidden input fields from HTML
func extractAllHiddenFields(bodyStr string) url.Values {
	form := url.Values{}

	// Match: <input type="hidden" name="X" value="Y">
	re1 := regexp.MustCompile(`(?i)<input[^>]*type\s*=\s*"hidden"[^>]*name\s*=\s*"([^"]+)"[^>]*value\s*=\s*"([^"]*)"`)
	for _, m := range re1.FindAllStringSubmatch(bodyStr, -1) {
		form.Set(m[1], m[2])
	}

	// Match: <input name="X" value="Y" type="hidden">
	re2 := regexp.MustCompile(`(?i)<input[^>]*name\s*=\s*"([^"]+)"[^>]*value\s*=\s*"([^"]*)"[^>]*type\s*=\s*"hidden"`)
	for _, m := range re2.FindAllStringSubmatch(bodyStr, -1) {
		if _, exists := form[m[1]]; !exists {
			form.Set(m[1], m[2])
		}
	}

	// Match: <input type="hidden" value="Y" name="X">
	re3 := regexp.MustCompile(`(?i)<input[^>]*type\s*=\s*"hidden"[^>]*value\s*=\s*"([^"]*)"[^>]*name\s*=\s*"([^"]+)"`)
	for _, m := range re3.FindAllStringSubmatch(bodyStr, -1) {
		if _, exists := form[m[2]]; !exists {
			form.Set(m[2], m[1])
		}
	}

	// Broader catch: any input with name and value (for SAML forms without type=hidden)
	re4 := regexp.MustCompile(`(?i)<input[^>]*name\s*=\s*"([^"]+)"[^>]*value\s*=\s*"([^"]*)"`)
	for _, m := range re4.FindAllStringSubmatch(bodyStr, -1) {
		if _, exists := form[m[1]]; !exists {
			form.Set(m[1], m[2])
		}
	}
	re5 := regexp.MustCompile(`(?i)<input[^>]*value\s*=\s*"([^"]*)"[^>]*name\s*=\s*"([^"]+)"`)
	for _, m := range re5.FindAllStringSubmatch(bodyStr, -1) {
		if _, exists := form[m[2]]; !exists {
			form.Set(m[2], m[1])
		}
	}

	return form
}

func hiddenFieldNames(form url.Values) []string {
	var names []string
	for k := range form {
		names = append(names, k)
	}
	return names
}

func resolveURL(baseURL, ref string) string {
	if strings.HasPrefix(ref, "http") {
		return ref
	}
	u, err := url.Parse(baseURL)
	if err != nil {
		return ref
	}
	refURL, err := url.Parse(ref)
	if err != nil {
		return ref
	}
	return u.ResolveReference(refURL).String()
}

func extractOrigin(rawURL string) string {
	u, err := url.Parse(rawURL)
	if err != nil {
		return rawURL
	}
	return u.Scheme + "://" + u.Host
}

// base64URLEncode encodes bytes to base64url without padding (per JWS/JWE spec)
func base64URLEncode(data []byte) string {
	return base64.RawURLEncoding.EncodeToString(data)
}

// hmacSHA256 computes HMAC-SHA256
func hmacSHA256(data, key []byte) []byte {
	h := hmac.New(sha256.New, key)
	h.Write(data)
	return h.Sum(nil)
}
