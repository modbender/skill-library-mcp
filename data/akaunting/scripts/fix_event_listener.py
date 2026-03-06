#!/usr/bin/env python3
"""
Fix Akaunting's broken event listener auto-discovery.

Akaunting's OfflinePayments module uses Laravel's event auto-discovery,
but it doesn't work properly. This script manually registers the listener.

Run after fresh Akaunting install or if you get "payment method is invalid" errors.
"""

import subprocess
import sys

CONTAINER_NAME = "akaunting"
EVENT_FILE = "/var/www/html/app/Providers/Event.php"

LISTENER_ENTRY = """        'App\\Events\\Module\\PaymentMethodShowing' => [
            'Modules\\OfflinePayments\\Listeners\\ShowAsPaymentMethod',
        ],"""

def run_docker(cmd: str) -> tuple[int, str]:
    """Run command in Docker container."""
    result = subprocess.run(
        ["docker", "exec", CONTAINER_NAME, "bash", "-c", cmd],
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout + result.stderr

def check_container():
    """Verify Akaunting container is running."""
    code, output = run_docker("echo ok")
    if code != 0:
        print(f"❌ Container '{CONTAINER_NAME}' not running or accessible")
        print(f"   Start with: docker compose up -d")
        sys.exit(1)
    print(f"✓ Container '{CONTAINER_NAME}' is running")

def check_already_fixed():
    """Check if fix was already applied."""
    code, output = run_docker(f"grep -q 'PaymentMethodShowing' {EVENT_FILE}")
    return code == 0

def apply_fix():
    """Apply the event listener fix."""
    # Create the sed command to insert after "$listen = ["
    sed_cmd = f"""sed -i "/protected \\$listen = \\[/a\\{LISTENER_ENTRY.replace(chr(10), chr(92) + 'n')}" {EVENT_FILE}"""
    
    # Simpler approach: use PHP to patch the file
    php_patch = f'''
$file = "{EVENT_FILE}";
$content = file_get_contents($file);

$listener = "        'App\\\\Events\\\\Module\\\\PaymentMethodShowing' => [
            'Modules\\\\OfflinePayments\\\\Listeners\\\\ShowAsPaymentMethod',
        ],";

// Insert after protected $listen = [
$content = preg_replace(
    '/(protected \\$listen = \\[)/',
    "$1\\n" . $listener,
    $content
);

file_put_contents($file, $content);
echo "Patched!";
'''
    
    code, output = run_docker(f"php -r '{php_patch}'")
    if code != 0 or "Patched!" not in output:
        print(f"❌ Failed to apply fix")
        print(f"   Error: {output}")
        return False
    return True

def clear_caches():
    """Clear Laravel caches."""
    commands = [
        "php artisan event:clear",
        "php artisan cache:clear",
        "php artisan config:clear"
    ]
    for cmd in commands:
        code, output = run_docker(f"cd /var/www/html && {cmd}")
        if code != 0:
            print(f"   Warning: {cmd} failed")

def main():
    print("Akaunting Event Listener Fix")
    print("=" * 40)
    
    check_container()
    
    if check_already_fixed():
        print("✓ Fix already applied")
        return
    
    print("Applying fix...")
    if apply_fix():
        print("✓ Event listener registered")
        
        print("Clearing caches...")
        clear_caches()
        print("✓ Caches cleared")
        
        print("\n✅ Fix complete! Transactions should work now.")
    else:
        print("\n❌ Fix failed. Apply manually:")
        print(f"   Edit {EVENT_FILE}")
        print("   Add to $listen array:")
        print(LISTENER_ENTRY)

if __name__ == "__main__":
    main()
