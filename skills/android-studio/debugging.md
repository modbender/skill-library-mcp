# Debugging — Android Studio

## Breakpoint Types

### Line Breakpoints
Standard breakpoint on a line. Execution pauses when reached.

### Conditional Breakpoints
Right-click breakpoint → add condition:
```kotlin
i > 100 && user.isActive
```
Only breaks when condition is true.

### Log Breakpoints
Right-click breakpoint → Suspend: unchecked, Log: checked
Logs expression without stopping:
```
"User: " + user.name + ", count: " + items.size()
```

### Exception Breakpoints
Run → View Breakpoints → Add (Exception)
- Caught exceptions: breaks on handled exceptions
- Uncaught exceptions: breaks on crashes
Filter by exception class for targeted debugging.

### Method Breakpoints
Set on method signature. Breaks on entry/exit.
Slower than line breakpoints. Use sparingly.

### Field Watchpoints
Set on field declaration. Breaks when field is read/modified.
Useful for tracking unexpected state changes.

## Debugger Features

### Evaluate Expression (Alt+F8)
Execute code in current context:
```kotlin
user.calculateScore()
items.filter { it.isValid }.size
```
Can modify state - be careful in production debugging.

### Watches
Add variables to track across frames:
- Right-click variable → Add to Watches
- Type expression in Watches panel
Watches evaluate in current context.

### Frames Panel
Navigate call stack:
- Click frame to see local variables at that point
- "Drop Frame" to re-execute from earlier point
- Filter out library frames for clarity

### Variables Panel
Inspect current scope:
- Expand objects to see fields
- Right-click to set value
- Mark object for tracking across scopes

### Inline Values
Values shown next to variables in editor.
Preferences → Debugger → Show values inline

## Debugging Strategies

### Reproduce First
Before debugging:
1. Identify exact reproduction steps
2. Confirm bug happens consistently
3. Note any conditions (device, API level, data state)

### Binary Search with Breakpoints
When bug location is unknown:
1. Set breakpoint at suspected midpoint
2. Check if bug already happened
3. Move breakpoint earlier or later
4. Repeat until found

### Logging Strategy
When breakpoints are impractical:
```kotlin
Log.d("DEBUG", "Method called: param=$param, state=$state")
```
Use Logcat filters:
- Filter by tag: `tag:DEBUG`
- Filter by package: `package:com.yourapp`

### Remote Debugging
For issues only on specific devices:
1. Enable USB debugging on device
2. Run → Attach Debugger to Android Process
3. Select device and process

## Common Debugging Scenarios

### Null Pointer Exceptions
1. Set exception breakpoint for NullPointerException
2. Check stack trace for origin
3. Inspect variables leading to null

### Race Conditions
1. Use thread-aware breakpoints
2. Check Frames panel for thread state
3. Add logging with thread ID:
```kotlin
Log.d("THREAD", "[${Thread.currentThread().name}] State: $state")
```

### UI Not Updating
1. Verify data changes reach UI layer
2. Check if running on main thread
3. In Compose: verify State objects are being read

### Memory Issues
1. Use Memory Profiler during reproduction
2. Take heap dump at problem moment
3. Analyze retained objects

### Slow Performance
1. CPU Profiler with sampling
2. Identify hot methods
3. Trace specific methods for detailed timing

## Logcat Tips

### Filtering
```
tag:MyTag level:error package:mine
```
Combine filters with spaces.

### Custom Filters
Logcat → Edit Filter Configuration
Save common filters for quick access.

### Clearing
Clear logs before reproduction for clean output.
Click trash icon or `adb logcat -c`

### Saving
Save logs for sharing or later analysis.
Click save icon in Logcat panel.

## Profiler Integration

### CPU Profiler
- Record during reproduction
- Analyze Call Chart for method timing
- Flame Graph for cumulative time
- Top Down for call hierarchy

### Memory Profiler
- Track allocations during reproduction
- Heap dump for leak analysis
- Compare dumps to find growth

### Network Profiler
- Timeline of network calls
- Response bodies and timing
- Identify slow or failing requests
