---
name: maven-central-publish
description: "Comprehensive guide and toolkit for publishing Java artifacts to Maven Central using the modern Central Portal (central.sonatype.com) workflow."
version: 1.0.0
metadata:
  openclaw:
    emoji: "📦"
    category: publishing
  clawhub:
    requires:
      bins: ["maven", "gpg"]
---

# Maven Central Publish Skill

This skill provides a standardized workflow for publishing Java/Kotlin libraries to the Maven Central Repository using the modern **Central Portal** (via `central-publishing-maven-plugin`).

## 📋 Prerequisites

1.  **Central Portal Account**: Sign up at [central.sonatype.com](https://central.sonatype.com/).
2.  **Namespace Verified**: You must have verified your `groupId` (e.g., `io.github.username` or `com.yourdomain`) in the portal.
3.  **User Token**: Generated from the Central Portal (My Account -> Generate User Token).

## 🛠️ Environment Setup

### 1. Install Tools
Ensure `maven`, `gnupg`, and `openjdk-17+` are installed.

```bash
# Ubuntu/Debian
apt-get install -y maven gnupg openjdk-17-jdk
```

### 2. GPG Configuration (Critical)
Maven requires GPG signing. For automated/headless environments, **Loopback Pinentry** is required.

```bash
# 1. Generate Key (if none exists)
gpg --gen-key

# 2. Configure Loopback (Prevent UI prompts)
mkdir -p ~/.gnupg
echo "allow-loopback-pinentry" >> ~/.gnupg/gpg-agent.conf
echo "pinentry-mode loopback" >> ~/.gnupg/gpg.conf
gpg-connect-agent reloadagent /bye

# 3. Publish Key
gpg --list-keys # Get your Key ID (last 8 chars or full hex)
gpg --keyserver keyserver.ubuntu.com --send-keys <KEY_ID>
```

### 3. Maven Settings (`~/.m2/settings.xml`)
Configure your Central Portal credentials.

```xml
<settings>
  <servers>
    <server>
      <id>central</id>
      <username>USER_TOKEN_USERNAME</username>
      <password>USER_TOKEN_PASSWORD</password>
    </server>
  </servers>
  <profiles>
    <profile>
      <id>release</id>
      <activation>
        <activeByDefault>false</activeByDefault>
      </activation>
      <properties>
        <gpg.executable>gpg</gpg.executable>
        <gpg.passphrase>YOUR_GPG_PASSPHRASE</gpg.passphrase>
      </properties>
    </profile>
  </profiles>
</settings>
```

## 📦 Project Configuration (`pom.xml`)

Your project **MUST** meet the [Quality Requirements](https://central.sonatype.org/publish/requirements/):
1.  **Coordinates**: `groupId`, `artifactId`, `version`.
2.  **Metadata**: `name`, `description`, `url`, `licenses`, `developers`, `scm`.
3.  **Plugins**: Javadoc, Source, GPG, and Central Publishing.

### Recommended Plugin Configuration

Add this to your `<build><plugins>` section:

```xml
<!-- 1. Source Plugin -->
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-source-plugin</artifactId>
    <version>3.3.0</version>
    <executions>
        <execution>
            <id>attach-sources</id>
            <goals><goal>jar-no-fork</goal></goals>
        </execution>
    </executions>
</plugin>

<!-- 2. Javadoc Plugin -->
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-javadoc-plugin</artifactId>
    <version>3.6.3</version>
    <configuration>
        <doclint>none</doclint> <!-- Prevent strict checks failing build -->
        <failOnError>false</failOnError>
    </configuration>
    <executions>
        <execution>
            <id>attach-javadocs</id>
            <goals><goal>jar</goal></goals>
        </execution>
    </executions>
</plugin>

<!-- 3. GPG Plugin (Best Practice: wrap in 'release' profile) -->
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-gpg-plugin</artifactId>
    <version>3.1.0</version>
    <configuration>
        <gpgArguments>
            <arg>--pinentry-mode</arg>
            <arg>loopback</arg>
        </gpgArguments>
    </configuration>
    <executions>
        <execution>
            <id>sign-artifacts</id>
            <phase>verify</phase>
            <goals><goal>sign</goal></goals>
        </execution>
    </executions>
</plugin>

<!-- 4. Central Publishing Plugin (The Magic Sauce) -->
<plugin>
    <groupId>org.sonatype.central</groupId>
    <artifactId>central-publishing-maven-plugin</artifactId>
    <version>0.7.0</version>
    <extensions>true</extensions>
    <configuration>
        <publishingServerId>central</publishingServerId>
        <!-- autoPublish: set to true to skip manual button click in portal -->
        <autoPublish>false</autoPublish> 
    </configuration>
</plugin>
```

## 🚀 Deployment

Run the deploy command with the `release` profile active:

```bash
mvn clean deploy -P release
```

**Success Indicators:**
- `[INFO] Uploaded bundle successfully...`
- `[INFO] Deployment ... has been validated.`

If `autoPublish` is false (recommended for first time), log in to [central.sonatype.com](https://central.sonatype.com/publishing/deployments), review the deployment, and click **Publish**.

## ❓ Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `401 Unauthorized` | Invalid User Token in `settings.xml` | Generate new token in Central Portal. Ensure server ID matches. |
| `GPG signing failed` | No pinentry / wrong passphrase | Use `pinentry-mode loopback` config; Check `gpg-agent`. |
| `Javadoc generation failed` | Strict HTML checks | Add `<doclint>none</doclint>` to javadoc plugin config. |
| `Invalid coordinates` | GroupId mismatch | Ensure `pom.xml` groupId matches verified namespace in Portal. |

