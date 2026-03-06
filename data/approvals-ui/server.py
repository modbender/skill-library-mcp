
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit
import os
import json
import subprocess
import time
import pty
import select
import threading
import fcntl
import termios
import struct
from pathlib import Path
from functools import wraps

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.absolute()

app = Flask(__name__, template_folder=str(SCRIPT_DIR / 'templates'))
# IMPORTANT: In a real application, this should be a strong, unique, and secret key,
# preferably loaded from environment variables or a secure config.
# For this example, we'll use a placeholder and assume it's handled securely.
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'a_very_secret_key_for_dev_only_change_me')

# Use threading mode for Socket.IO (eventlet is deprecated)
# For production, consider using gevent or uWSGI with gevent
async_mode = 'threading'

# Force polling transport only — Werkzeug's dev server doesn't support WebSocket
# with threading async_mode, and the failed upgrade spams ugly 500 errors in the console.
socketio = SocketIO(app, cors_allowed_origins="*", async_mode=async_mode, transports=['polling'])

# In-memory storage for pairings (for simplicity)
# In a real app, use a database or more persistent storage.
pairings = []

# OpenClaw state directory (default location)
OPENCLAW_STATE_DIR = Path(os.environ.get('OPENCLAW_STATE_DIR', os.path.expanduser('~/.openclaw')))

def get_gateway_token():
    """Read the gateway auth token from openclaw.json."""
    config_file = OPENCLAW_STATE_DIR / 'openclaw.json'
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config.get('gateway', {}).get('auth', {}).get('token', '')
    except Exception:
        return ''

def load_pairings_from_files():
    """Load channel pairings directly from OpenClaw's pairing JSON files."""
    global pairings
    loaded_count = 0
    
    # Scan all *-pairing.json files in the credentials directory
    credentials_dir = OPENCLAW_STATE_DIR / 'credentials'
    if credentials_dir.exists():
        for pairing_file in credentials_dir.glob('*-pairing.json'):
            try:
                with open(pairing_file, 'r') as f:
                    file_data = json.load(f)
                    channel_name = pairing_file.stem.replace('-pairing', '')
                    
                    requests = file_data.get('requests', [])
                    for req in requests:
                        pairing_data = {
                            'channel_id': channel_name,
                            'code': req.get('code', ''),
                            'user_id': req.get('id', ''),
                            'device_name': f"{req.get('meta', {}).get('firstName', '')} {req.get('meta', {}).get('lastName', '')}".strip() or req.get('meta', {}).get('username', 'Unknown'),
                            'timestamp': req.get('createdAt', ''),
                            'meta': req.get('meta', {})
                        }
                        # Avoid duplicates
                        if not any(p.get('code') == pairing_data['code'] for p in pairings):
                            pairings.append(pairing_data)
                            loaded_count += 1
                            print(f"Loaded channel pairing: {pairing_data['code']} from {channel_name}")
            except Exception as e:
                print(f"Error loading {pairing_file}: {e}")
    
    if loaded_count > 0:
        print(f"Loaded {loaded_count} channel pairings from files")
    else:
        print("No pending channel pairing requests found (all channels already paired)")
    
    return loaded_count


def load_device_pairings_from_files():
    """Load device pairings directly from OpenClaw's device JSON files."""
    devices_dir = OPENCLAW_STATE_DIR / 'devices'
    pending = []
    paired = []
    
    pending_file = devices_dir / 'pending.json'
    paired_file = devices_dir / 'paired.json'
    
    if pending_file.exists():
        try:
            with open(pending_file, 'r') as f:
                data = json.load(f)
                pending = list(data.values()) if isinstance(data, dict) else data
                print(f"Loaded {len(pending)} pending device pairing(s) from file")
        except Exception as e:
            print(f"Error loading {pending_file}: {e}")
    
    if paired_file.exists():
        try:
            with open(paired_file, 'r') as f:
                data = json.load(f)
                paired = list(data.values()) if isinstance(data, dict) else data
                print(f"Loaded {len(paired)} paired device(s) from file")
        except Exception as e:
            print(f"Error loading {paired_file}: {e}")
    
    return {
        "pending": sorted(pending, key=lambda x: x.get('ts', 0), reverse=True),
        "paired": sorted(paired, key=lambda x: x.get('approvedAtMs', 0), reverse=True)
    }


# --- Authentication ---
# Login credentials
ADMIN_USERNAME = 'Drinnas'
ADMIN_PASSWORD = 'admin'
AUTH_PASSWORD = os.environ.get('SERVER_AUTH_PASSWORD', 'Bb7766!server') # Defaulting to user's provided password

def authenticate(password):
    # In a real app, you'd do more than just compare a string password.
    # This could involve hashing, tokens, etc.
    return password == AUTH_PASSWORD

def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---

@app.route('/')
def index():
    """Redirect to login if not authenticated, otherwise to dashboard."""
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    # If already logged in, redirect to dashboard
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout and clear session."""
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard page."""
    return render_template('dashboard.html')

@app.route('/channel-approvals')
@login_required
def channel_approvals():
    """Channel approvals tab."""
    return render_template('channel_approvals.html')

@app.route('/terminal')
@login_required
def terminal():
    """Terminal tab."""
    return render_template('terminal.html')

@app.route('/pair', methods=['POST'])
def add_pairing():
    # Endpoint to register a new pairing.
    # Expects a JSON body with pairing details and a password for auth.
    # Example payload:
    # {
    #   "password": "Bb7766!server",
    #   "pairing": {
    #     "channel_id": "some_channel_id",
    #     "device_name": "My Device",
    #     "timestamp": "2023-10-27T10:30:00Z"
    #   }
    # }
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    password = data.get('password')
    if not authenticate(password):
        return jsonify({"error": "Authentication failed"}), 401

    pairing_data = data.get('pairing')
    if not pairing_data:
        return jsonify({"error": "Missing 'pairing' data in payload"}), 400

    # Avoid duplicates (check by code if available)
    pairing_code = pairing_data.get('code')
    if pairing_code and any(p.get('code') == pairing_code for p in pairings):
        return jsonify({"message": "Pairing already exists", "pairing": pairing_data}), 200

    # Add pairing to our list
    pairings.append(pairing_data)
    print(f"New pairing registered: {pairing_data}")

    # Broadcast the new pairing to all connected clients
    socketio.emit('new_pairing', pairing_data)
    
    return jsonify({"message": "Pairing registered successfully", "pairing": pairing_data}), 201

@app.route('/sync', methods=['POST'])
def sync_pairings():
    """Sync pairings from OpenClaw to the server."""
    data = request.get_json() or {}
    password = data.get('password')
    
    if not authenticate(password):
        return jsonify({"error": "Authentication failed"}), 401
    
    loaded_count = load_pairings_from_files()
    
    # Broadcast all pairings to connected clients
    for pairing in pairings:
        socketio.emit('new_pairing', pairing)
    
    return jsonify({"message": f"Synced {loaded_count} pairings from OpenClaw", "total": len(pairings)}), 200

@app.route('/approve', methods=['POST'])
@login_required
def approve_pairing():
    """Approve a pairing in OpenClaw."""
    global pairings
    
    data = request.get_json() or {}
    password = data.get('password')
    code = data.get('code')
    channel = data.get('channel')
    notify = data.get('notify', False)
    
    if not authenticate(password):
        return jsonify({"error": "Authentication failed"}), 401
    
    if not code:
        return jsonify({"error": "Missing 'code' in payload"}), 400
    
    if not channel:
        return jsonify({"error": "Missing 'channel' in payload"}), 400
    
    # Helper function to check if pairing was actually approved
    def check_if_approved():
        """Check if the pairing code no longer exists in the pairing file."""
        pairing_file = OPENCLAW_STATE_DIR / 'credentials' / f'{channel}-pairing.json'
        if pairing_file.exists():
            try:
                with open(pairing_file, 'r') as f:
                    file_data = json.load(f)
                    requests = file_data.get('requests', [])
                    # Check if the code is no longer in the requests (meaning it was approved)
                    return not any(req.get('code') == code for req in requests)
            except Exception as e:
                print(f"Error checking pairing file: {e}")
        return False
    
    # Helper function to remove pairing and notify clients
    def remove_pairing_and_notify():
        """Remove pairing from list and notify clients."""
        global pairings
        pairings = [p for p in pairings if p.get('code') != code]
        socketio.emit('pairing_approved', {'code': code})
        print(f"Removed pairing {code} from list and notified clients")
    
    try:
        # Call OpenClaw approve command
        cmd = ['openclaw', 'pairing', 'approve', '--channel', channel, code]
        if notify:
            cmd.append('--notify')
        
        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30  # Increased timeout to 30 seconds
        )
        
        print(f"Command exit code: {result.returncode}")
        print(f"Command stdout: {result.stdout}")
        print(f"Command stderr: {result.stderr}")
        
        # Check if pairing was actually approved (even if command failed)
        if check_if_approved():
            remove_pairing_and_notify()
            if result.returncode == 0:
                return jsonify({
                    "message": f"Pairing {code} approved successfully",
                    "output": result.stdout
                }), 200
            else:
                # Command failed but pairing was approved (maybe manually or by another process)
                return jsonify({
                    "message": f"Pairing {code} was approved (command had errors but pairing is gone)",
                    "warning": result.stderr or "Command returned non-zero exit code",
                    "output": result.stdout
                }), 200
        
        if result.returncode == 0:
            # Command succeeded but pairing still exists? Remove it anyway
            remove_pairing_and_notify()
            return jsonify({
                "message": f"Pairing {code} approved successfully",
                "output": result.stdout
            }), 200
        else:
            # Command failed and pairing still exists
            return jsonify({
                "error": f"Failed to approve pairing: {result.stderr or 'Unknown error'}",
                "output": result.stdout
            }), 400
            
    except subprocess.TimeoutExpired as e:
        print(f"Command timed out: {e}")
        # Even if timeout, check if the pairing was actually approved
        time.sleep(1)  # Give it a moment to complete
        
        if check_if_approved():
            remove_pairing_and_notify()
            return jsonify({
                "message": f"Pairing {code} approved successfully (timeout but completed)",
                "warning": "Command timed out but pairing was approved"
            }), 200
        else:
            return jsonify({
                "error": "OpenClaw CLI timeout - pairing may still be pending",
                "message": "The approval command timed out. Please check manually or try again."
            }), 500
    except FileNotFoundError:
        print("OpenClaw CLI not found")
        # Check if pairing was approved anyway (maybe manually)
        if check_if_approved():
            remove_pairing_and_notify()
            return jsonify({
                "message": f"Pairing {code} was approved (CLI not found but pairing is gone)",
                "warning": "OpenClaw CLI not found"
            }), 200
        return jsonify({"error": "OpenClaw CLI not found"}), 500
    except Exception as e:
        print(f"Unexpected error approving pairing: {e}")
        import traceback
        traceback.print_exc()
        # Check if pairing was approved anyway
        if check_if_approved():
            remove_pairing_and_notify()
            return jsonify({
                "message": f"Pairing {code} was approved (error occurred but pairing is gone)",
                "warning": f"Error: {str(e)}"
            }), 200
        return jsonify({"error": f"Error approving pairing: {str(e)}"}), 500


# --- Device Pairing (Browser Connections) ---

@app.route('/device-pairings')
@login_required
def device_pairings_page():
    """Device pairings management page."""
    return render_template('device_pairings.html', gateway_token=get_gateway_token())

@app.route('/api/device-pairings', methods=['GET'])
@login_required
def list_device_pairings():
    """List pending and paired device pairings by reading files directly."""
    try:
        data = load_device_pairings_from_files()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/device-pair/approve', methods=['POST'])
@login_required
def approve_device_pairing():
    """Approve a pending device pairing request."""
    data = request.get_json() or {}
    request_id = data.get('requestId')
    use_latest = data.get('latest', False)

    if not request_id and not use_latest:
        return jsonify({"error": "Missing 'requestId' or set 'latest' to true"}), 400

    try:
        cmd = ['openclaw', 'devices', 'approve', '--json']
        if use_latest:
            cmd.append('--latest')
        else:
            cmd.append(request_id)

        print(f"Running device approve command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=15
        )

        print(f"Device approve exit code: {result.returncode}")
        print(f"Device approve stdout: {result.stdout}")
        print(f"Device approve stderr: {result.stderr}")

        if result.returncode == 0:
            try:
                response_data = json.loads(result.stdout)
            except json.JSONDecodeError:
                response_data = {"output": result.stdout}

            # Notify connected clients
            socketio.emit('device_pairing_approved', {
                'requestId': request_id or 'latest',
                'data': response_data
            })

            return jsonify({
                "message": "Device pairing approved successfully",
                "data": response_data
            }), 200
        else:
            return jsonify({
                "error": f"Failed to approve device pairing: {result.stderr or result.stdout or 'Unknown error'}"
            }), 400

    except subprocess.TimeoutExpired:
        return jsonify({"error": "OpenClaw CLI timeout during approval"}), 500
    except FileNotFoundError:
        return jsonify({"error": "OpenClaw CLI not found"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/device-pair/reject', methods=['POST'])
@login_required
def reject_device_pairing():
    """Reject a pending device pairing request."""
    data = request.get_json() or {}
    request_id = data.get('requestId')

    if not request_id:
        return jsonify({"error": "Missing 'requestId'"}), 400

    try:
        cmd = ['openclaw', 'devices', 'reject', '--json', request_id]

        print(f"Running device reject command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode == 0:
            try:
                response_data = json.loads(result.stdout)
            except json.JSONDecodeError:
                response_data = {"output": result.stdout}

            socketio.emit('device_pairing_rejected', {
                'requestId': request_id,
                'data': response_data
            })

            return jsonify({
                "message": "Device pairing rejected",
                "data": response_data
            }), 200
        else:
            return jsonify({
                "error": f"Failed to reject device pairing: {result.stderr or result.stdout or 'Unknown error'}"
            }), 400

    except subprocess.TimeoutExpired:
        return jsonify({"error": "OpenClaw CLI timeout during rejection"}), 500
    except FileNotFoundError:
        return jsonify({"error": "OpenClaw CLI not found"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/device-pair/approve-latest', methods=['POST'])
@login_required
def approve_latest_device_pairing():
    """Quick endpoint to approve the most recent pending device pairing."""
    try:
        result = subprocess.run(
            ['openclaw', 'devices', 'approve', '--latest', '--json'],
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode == 0:
            try:
                response_data = json.loads(result.stdout)
            except json.JSONDecodeError:
                response_data = {"output": result.stdout}

            socketio.emit('device_pairing_approved', {
                'requestId': 'latest',
                'data': response_data
            })

            return jsonify({
                "message": "Latest device pairing approved",
                "data": response_data
            }), 200
        else:
            return jsonify({
                "error": f"Failed: {result.stderr or result.stdout or 'No pending requests'}"
            }), 400

    except subprocess.TimeoutExpired:
        return jsonify({"error": "CLI timeout"}), 500
    except FileNotFoundError:
        return jsonify({"error": "OpenClaw CLI not found"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Terminal Connection ---
import paramiko
# Function to connect to a live terminal on your Mac

def connect_terminal():
    # Connect to the terminal using paramiko
    hostname = 'your_mac_ip'
    username = 'your_username'
    password = 'your_password'
    port = 22  # Adjust based on your SSH configuration

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname, username=username, password=password, port=port)
        # Now you can run commands in the terminal
        return client
    except Exception as e:
        print(f'Failed to connect to terminal: {e}')

@socketio.on('connect')
def handle_connect():
    print('Client connected. Syncing pairings from files...')
    # Load channel pairings from files
    load_pairings_from_files()
    # Load device pairings from files
    device_data = load_device_pairings_from_files()
    print(f'Sending {len(pairings)} channel pairings and {len(device_data.get("pending", []))} pending / {len(device_data.get("paired", []))} paired devices to client.')
    # Send existing pairings to the newly connected client
    emit('initial_pairings', {'pairings': pairings, 'device_pairings': device_data})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    # Clean up terminal session if it exists
    try:
        _cleanup_terminal(request.sid)
    except Exception:
        pass

# --- Terminal Support ---
# Store terminal processes per session
terminal_processes = {}

def get_shell():
    """Get the user's default shell."""
    shell = os.environ.get('SHELL', '/bin/zsh')
    if not os.path.exists(shell):
        shell = '/bin/bash'
    return shell

@socketio.on('terminal_connect')
def handle_terminal_connect():
    """Initialize a new terminal session using subprocess (avoids fork warnings)."""
    sid = request.sid
    shell = get_shell()
    
    print(f'Terminal connect requested for {sid}, shell: {shell}')
    
    # Check if terminal already exists for this session
    if sid in terminal_processes:
        print(f'Terminal already exists for {sid}, cleaning up first')
        _cleanup_terminal(sid)
    
    try:
        # Create a pseudo-terminal
        master_fd, slave_fd = pty.openpty()
        
        # Use subprocess instead of fork to avoid "multi-threaded fork" warnings
        env = os.environ.copy()
        env['TERM'] = 'xterm-256color'
        env['COLORTERM'] = 'truecolor'
        
        process = subprocess.Popen(
            [shell],
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            start_new_session=True,
            env=env
        )
        os.close(slave_fd)
        
        terminal_processes[sid] = {
            'pid': process.pid,
            'fd': master_fd,
            'process': process,
            'closing': False
        }
        
        # Start thread to read from terminal
        def read_terminal():
            try:
                while sid in terminal_processes and not terminal_processes[sid].get('closing'):
                    try:
                        readable, _, _ = select.select([master_fd], [], [], 0.1)
                    except (OSError, ValueError):
                        break  # fd closed, exit quietly
                    if master_fd in readable:
                        try:
                            data = os.read(master_fd, 1024)
                            if data:
                                socketio.emit('terminal_output', {'data': data.decode('utf-8', errors='replace')}, room=sid)
                            else:
                                break  # EOF
                        except (OSError, ValueError):
                            break  # fd closed, exit quietly
            except Exception:
                pass  # Suppress all terminal read errors on shutdown
            finally:
                # Only clean up if we haven't been cleaned up already
                if sid in terminal_processes and not terminal_processes[sid].get('closing'):
                    _cleanup_terminal(sid)
        
        thread = threading.Thread(target=read_terminal, daemon=True)
        thread.start()
        terminal_processes[sid]['thread'] = thread
        
        emit('terminal_ready')
        print(f'Terminal session started for {sid} (PID {process.pid})')
    except Exception as e:
        print(f'Error starting terminal: {e}')
        emit('terminal_error', {'message': f'Failed to start terminal: {str(e)}'})

@socketio.on('terminal_input')
def handle_terminal_input(data):
    """Handle input from the terminal."""
    sid = request.sid
    if sid in terminal_processes:
        try:
            fd = terminal_processes[sid]['fd']
            input_data = data.get('data', '')
            if isinstance(input_data, str):
                input_data = input_data.encode('utf-8')
            os.write(fd, input_data)
        except Exception as e:
            print(f'Error writing to terminal: {e}')
            emit('terminal_error', {'message': str(e)})

@socketio.on('terminal_resize')
def handle_terminal_resize(data):
    """Handle terminal resize."""
    sid = request.sid
    if sid in terminal_processes:
        try:
            fd = terminal_processes[sid]['fd']
            cols = data.get('cols', 80)
            rows = data.get('rows', 24)
            
            # Set terminal size
            size = struct.pack('HHHH', rows, cols, 0, 0)
            fcntl.ioctl(fd, termios.TIOCSWINSZ, size)
        except Exception as e:
            print(f'Error resizing terminal: {e}')

def _cleanup_terminal(sid):
    """Safely clean up a terminal session. Can be called from any thread."""
    if sid not in terminal_processes:
        return
    info = terminal_processes.pop(sid, None)
    if not info or info.get('closing'):
        return
    info['closing'] = True
    
    # Close the PTY fd
    try:
        os.close(info['fd'])
    except OSError:
        pass
    
    # Terminate the subprocess
    proc = info.get('process')
    if proc:
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
    
    print(f'Terminal session cleaned up for {sid}')


@socketio.on('terminal_disconnect')
def handle_terminal_disconnect():
    """Clean up terminal session."""
    _cleanup_terminal(request.sid)

# --- Helper for running the server ---
if __name__ == '__main__':
    # Ensure templates directory exists for render_template
    templates_dir = SCRIPT_DIR / 'templates'
    if not templates_dir.exists():
        templates_dir.mkdir(parents=True, exist_ok=True)

    # Templates are now stored as separate files in the templates directory
    # No need to generate index.html dynamically

    # Load pairings from files on startup (will also sync on each client connect)
    print("Loading pairings from files on startup...")
    load_pairings_from_files()
    device_data = load_device_pairings_from_files()
    print(f"Startup: {len(device_data.get('pending', []))} pending device(s), {len(device_data.get('paired', []))} paired device(s)")
    
    print("Starting Flask server on http://127.0.0.1:9100")
    # Use socketio.run for Flask-SocketIO
    # async_mode='threading' works with Werkzeug, but eventlet/gevent is better for production
    # host='0.0.0.0' makes it accessible from other machines on the network
    # debug=True is useful for development, but should be False in production
    socketio.run(app, host='127.0.0.1', port=9100, debug=True, allow_unsafe_werkzeug=True)
