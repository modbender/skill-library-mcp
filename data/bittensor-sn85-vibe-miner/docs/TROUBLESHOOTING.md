# Troubleshooting Guide

## Common Issues and Solutions

### Compressor Crash Loop

**Symptoms:**
- PM2 shows video-compressor restarting constantly
- High restart count (↺ column)

**Diagnosis:**
```bash
pm2 logs video-compressor --lines 50
```

**Common Causes:**

1. **Python Syntax Error (usually VMAF patch)**
   - Look for `IndentationError` or `SyntaxError`
   - **Fix:** Re-apply patch carefully or restore from backup
   ```bash
   cd ~/vidaio-subnet/services/compress
   cp validator_merger.py.backup validator_merger.py
   patch -p3 < ~/.agents/skills/bittensor-sn85-vibe-miner/patches/validator_merger_vmaf.patch
   pm2 restart video-compressor
   ```

2. **Missing Dependencies**
   - Look for `ModuleNotFoundError`
   - **Fix:** Reinstall dependencies
   ```bash
   cd ~/vidaio-subnet
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Port Conflict**
   - Look for `Address already in use`
   - **Fix:** Change port in startup script or kill conflicting process

---

### Low Incentive / Rank Decline

**Symptoms:**
- Incentive dropping despite completing tasks
- Rank steadily declining

**Diagnosis:**
Check if VMAF calculation is running:
```bash
pm2 logs video-compressor | grep -E "Calculating final video VMAF|Skipping full video VMAF"
```

**If you see "Skipping":**
- ❌ **VMAF patch not applied correctly**
- This is the #1 cause of rank decline
- Validators score based on measured quality
- Without VMAF, you're submitting unverified videos

**Fix:**
```bash
cd ~/vidaio-subnet/services/compress
# Verify patch applied
grep -A5 "if calculate_full_video_vmaf:" validator_merger.py

# If not found, apply patch
patch -p3 < ~/.agents/skills/bittensor-sn85-vibe-miner/patches/validator_merger_vmaf.patch
pm2 restart video-compressor
```

**If you see "Calculating":**
- ✅ VMAF is working
- Rank decline may be due to:
  - Better competitors joining
  - Video2x performance (check processing times)
  - Network connectivity issues
  - Validator selection randomness

---

### No Tasks Received

**Upscaler:**
Expected frequency: 30-60 minutes

**Compressor:**
Expected frequency: 1-2 hours (sometimes longer gaps)

**If no tasks for >3 hours:**

1. **Check axon registration:**
   ```bash
   btcli subnet list --netuid 85 --wallet.name default --subtensor.network finney
   ```
   Should show your UIDs with correct IPs/ports

2. **Test connectivity:**
   ```bash
   # Get your external IP
   curl -4 icanhazip.com
   
   # Test axon (should get 404 with available synapses listed)
   curl -I http://<your_ip>:<your_port>
   ```

3. **Check PM2 logs:**
   ```bash
   pm2 logs video-miner --lines 100
   ```
   Look for connection errors or validator rejections

4. **Vast.ai port mapping:**
   ```bash
   # Verify environment variables
   env | grep VAST_TCP_PORT
   
   # Should see mappings like:
   # VAST_TCP_PORT_8384=<external_port>
   ```

---

### Deregistration Risk

**Warning Signs:**
- Incentive < 0.002
- Rank > 230/256
- Multiple days without improvement

**Immediate Actions:**

1. **Verify VMAF is active** (see above)

2. **Check task completion:**
   ```bash
   # Upscaler tasks
   tail -100 /root/.pm2/logs/video-miner-error.log | grep "Receiving.*Request" | wc -l
   
   # Compressor tasks
   tail -100 /root/.pm2/logs/video-miner-compress-error.log | grep "Receiving CompressionRequest" | wc -l
   ```

3. **GPU health:**
   ```bash
   nvidia-smi
   # Check temperature, utilization, errors
   ```

4. **Priority decision:**
   - Upscaler has better task frequency
   - If capital limited, focus on upscaler only
   - Compressor is lower priority but still profitable

**If deregistration imminent:**
- Consider voluntary deregistration to recover stake (0.13 τ)
- Re-register with fixes in place
- Registration cost same either way

---

### Video2x Too Slow

**Symptoms:**
- Upscaler tasks timing out
- Processing time >60 seconds for small videos
- Low incentive despite receiving tasks

**Diagnosis:**
```bash
which video2x
# Should be: /usr/local/bin/video2x (CLI binary)

video2x --version
# Should be: 6.3.1 or newer

# Check if Python version is being used instead
ps aux | grep video2x
```

**Fix if using Python version:**
```bash
# Remove Python version
pip uninstall video2x

# Install CLI binary
cd /tmp
curl -sL https://github.com/k4yt3x/video2x/releases/download/6.3.1/video2x-linux-amd64.zip -o video2x.zip
unzip video2x.zip
sudo mv video2x /usr/local/bin/
sudo chmod +x /usr/local/bin/video2x
rm video2x.zip

# Restart miner
pm2 restart video-miner
```

**Verify speed:**
Test with sample video:
```bash
time video2x -i test.mp4 -o test_upscaled.mp4 -m realesr-animevideov3
# Should complete 480p→1080p in <20 seconds
```

---

### Vast.ai Port Conflicts

**Occupied ports on Vast.ai:**
- 8080: Jupyter Notebook
- 11111: Vast.ai Instance Portal  
- 18384: Syncthing GUI

**Symptoms:**
- "Address already in use" errors
- Miners can't bind to ports

**Fix:**
Use alternative ports in start_miners.sh:
- Upscaler: 8384 (internal) → mapped external
- Compressor: 1111 (internal) → mapped external

**Never use:** 8080, 11111, 18384

---

### Storage Upload Failures

**BackBlaze B2:**

1. **Check credentials:**
   ```bash
   source ~/.sn85_storage_config
   echo $B2_BUCKET_NAME
   echo $B2_APPLICATION_KEY_ID
   ```

2. **Test upload:**
   ```bash
   # Install AWS CLI (B2 is S3-compatible)
   pip install awscli
   
   # Configure
   aws configure set aws_access_key_id $B2_APPLICATION_KEY_ID
   aws configure set aws_secret_access_key $B2_APPLICATION_KEY
   
   # Test
   echo "test" > test.txt
   aws s3 cp test.txt s3://$B2_BUCKET_NAME/ --endpoint-url https://$B2_ENDPOINT
   ```

3. **Check miner config:**
   Verify storage credentials in miner config files

**Hippius:**

1. **Verify S3 endpoint:**
   ```bash
   curl -I $HIPPIUS_ENDPOINT
   ```

2. **Check credentials:**
   Test with s3cmd or aws CLI

---

### GPU Not Detected / NVENC Issues

**Check NVIDIA driver:**
```bash
nvidia-smi
# Should show your GPU

# Check NVENC support
nvidia-smi --query-gpu=encoder.stats.sessionCount --format=csv,noheader
```

**If driver missing:**
```bash
# Ubuntu 22.04
sudo apt update
sudo apt install nvidia-driver-535 nvidia-utils-535
sudo reboot
```

**If NVENC not working:**
- Verify GPU model supports NVENC (RTX series yes, GTX limited)
- Check ffmpeg has nvenc support:
  ```bash
  ffmpeg -encoders | grep nvenc
  ```

---

### Memory Issues

**Symptoms:**
- Out of memory errors
- System freezing
- Killed processes

**Solutions:**

1. **Reduce concurrent tasks:**
   Edit miner config, limit parallel processing

2. **Increase swap:**
   ```bash
   sudo fallocate -l 8G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

3. **Monitor usage:**
   ```bash
   htop
   watch -n 1 free -h
   ```

---

## Getting Help

**Logs to check:**
```bash
# All miners
pm2 logs

# Specific miner
pm2 logs video-miner
pm2 logs video-compressor

# System
dmesg | tail -50
journalctl -xe
```

**Community:**
- Bittensor Discord: https://discord.gg/bittensor
- SN85 specific channels

**This skill:**
Built from real debugging experience. Most issues covered here were encountered and solved during development.
