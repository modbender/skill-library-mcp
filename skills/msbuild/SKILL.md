# Skill: Top 80 MSBuild Commands for .NET / ASP.NET (CLI)

## Purpose
This skill provides a practical, **prioritized** set of the **80 most useful command templates** for working with .NET / ASP.NET projects on the command line using **MSBuild** (via `dotnet msbuild` or `msbuild`). It mirrors a realistic day-to-day workflow: restore → build → test → publish/pack → diagnose → CI hardening.

## Typical ASP.NET Developer Workflow (why these commands are prioritized)
A typical ASP.NET CLI workflow:
1. **Restore** dependencies (often locked mode in CI)
2. **Build** quickly (Debug) and reliably (Release)
3. **Test** repeatedly (filters, logs, results dirs, no-build/no-restore in CI)
4. **Publish** artifacts (RID, self-contained, single-file, trimming, ready-to-run)
5. **Package** libraries (Pack), versioning
6. **Diagnose** build issues (binlog, verbosity, preprocess, graph build)
7. **CI hardening** (determinism, CI flags, node reuse, parallelism, reproducibility)

Ranking reflects frequency + impact in that flow.

## Conventions
- Prefer cross-platform: `dotnet msbuild`
- On Windows with VS Build Tools you can swap to: `msbuild`
- Targets: `/t:<Target>`
- Properties: `/p:Name=Value`
- Logging: `/v:<level>`, `/bl[:file]`, `/fl`, `/pp`
- Multiproc: `/m[:n]`
- Note: `dotnet test` is included because it is the practical test CLI (it invokes MSBuild under the hood).

---

## Top 80 Commands (1 = most important)

> Replace `MySolution.sln` / `src/MyWeb/MyWeb.csproj` / `tests/...` as needed.

### A) Restore / Build / Clean / Rebuild (daily)
1) Restore solution
```bash
dotnet msbuild MySolution.sln /t:Restore
```

2) Build solution (Debug)

```bash
dotnet msbuild MySolution.sln /t:Build /p:Configuration=Debug
```

3) Build solution (Release)

```bash
dotnet msbuild MySolution.sln /t:Build /p:Configuration=Release
```

4) Clean solution

```bash
dotnet msbuild MySolution.sln /t:Clean /p:Configuration=Debug
```

5) Rebuild solution (Clean + Build)

```bash
dotnet msbuild MySolution.sln /t:Rebuild /p:Configuration=Release
```

6) Restore + Build in one call

```bash
dotnet msbuild MySolution.sln /restore /t:Build /p:Configuration=Debug
```

7) Build without restore (CI-friendly)

```bash
dotnet msbuild MySolution.sln /t:Build /p:Configuration=Release /p:Restore=false
```

8) Parallel build (max CPU)

```bash
dotnet msbuild MySolution.sln /t:Build /m /p:Configuration=Release
```

9) Quiet-ish CI output

```bash
dotnet msbuild MySolution.sln /t:Build /nologo /v:minimal /p:Configuration=Release
```

10) Build a single project

```bash
dotnet msbuild src/MyWeb/MyWeb.csproj /t:Build /p:Configuration=Debug
```

11) Set Platform explicitly

```bash
dotnet msbuild MySolution.sln /t:Build /p:Configuration=Release /p:Platform="Any CPU"
```

12) Treat warnings as errors

```bash
dotnet msbuild MySolution.sln /t:Build /p:Configuration=Release /p:TreatWarningsAsErrors=true
```

13) Deterministic build

```bash
dotnet msbuild MySolution.sln /t:Build /p:Configuration=Release /p:Deterministic=true
```

14) CI build mode (SourceLink/versioning behavior)

```bash
dotnet msbuild MySolution.sln /t:Build /p:Configuration=Release /p:ContinuousIntegrationBuild=true
```

15) Disable incremental up-to-date checks (force build behavior)

```bash
dotnet msbuild MySolution.sln /t:Build /p:Configuration=Release /p:DisableFastUpToDateCheck=true
```

16) Build with defined constants

```bash
dotnet msbuild src/MyWeb/MyWeb.csproj /t:Build /p:Configuration=Debug /p:DefineConstants="TRACE;DEBUG;MYFLAG"
```

17) Set OutputPath (ad-hoc artifacts)

```bash
dotnet msbuild src/MyWeb/MyWeb.csproj /t:Build /p:Configuration=Release /p:OutputPath=artifacts/bin/
```

18) Set BaseIntermediateOutputPath (obj isolation / CI caching)

```bash
dotnet msbuild src/MyWeb/MyWeb.csproj /t:Build /p:Configuration=Release /p:BaseIntermediateOutputPath=artifacts/obj/
```

19) Disable shared compilation (debug odd build behavior)

```bash
dotnet msbuild MySolution.sln /t:Build /p:Configuration=Debug /p:UseSharedCompilation=false
```

20) Show MSBuild version

```bash
dotnet msbuild -version
```

### B) Tests (practical CLI; MSBuild-based)

21) Run tests (solution)

```bash
dotnet test MySolution.sln -c Release
```

22) Tests without build

```bash
dotnet test MySolution.sln -c Release --no-build
```

23) Tests without restore

```bash
dotnet test MySolution.sln -c Release --no-restore
```

24) Test a single test project

```bash
dotnet test tests/MyWeb.Tests/MyWeb.Tests.csproj -c Debug
```

25) Test filter by fully qualified name

```bash
dotnet test MySolution.sln -c Release --filter "FullyQualifiedName~MyNamespace"
```

26) Test filter by trait/category (example)

```bash
dotnet test MySolution.sln -c Release --filter "TestCategory=Integration"
```

27) TRX logger

```bash
dotnet test MySolution.sln -c Release --logger "trx"
```

28) Results directory

```bash
dotnet test MySolution.sln -c Release --results-directory artifacts/testresults
```

29) Collect coverage (cross-platform collector)

```bash
dotnet test MySolution.sln -c Release --collect "XPlat Code Coverage"
```

30) Increase test verbosity

```bash
dotnet test MySolution.sln -c Release -v normal
```

31) Blame/hang diagnostics

```bash
dotnet test MySolution.sln -c Release --blame
```

32) Run a specific test by name

```bash
dotnet test MySolution.sln -c Release --filter "Name=MySpecificTest"
```

### C) Publish (ASP.NET core scenarios)

33) Publish (Release, framework-dependent)

```bash
dotnet msbuild src/MyWeb/MyWeb.csproj /t:Publish /p:Configuration=Release
```

34) Publish to a specific directory

```bash
dotnet msbuild src/MyWeb/MyWeb.csproj /t:Publish /p:Configuration=Release /p:PublishDir=artifacts/publish/
```

35) Publish with RuntimeIdentifier (RID)

```bash
dotnet msbuild src/MyWeb/MyWeb.csproj /t:Publish /p:Configuration=Release /p:RuntimeIdentifier=linux-x64
```

36) Self-contained publish

```bash
dotnet msbuild src/MyWeb/MyWeb.csproj /t:Publish /p:Configuration=Release /p:RuntimeIdentifier=linux-x64 /p:SelfContained=true
```

37) Framework-dependent (explicit)

```bash
dotnet msbuild src/MyWeb/MyWeb.csproj /t:Publish /p:Configuration=Release /p:SelfContained=false
```

38) Single-file publish

```bash
dotnet msbuild src/MyWeb/MyWeb.csproj /t:Publish /p:Configuration=Release /p:RuntimeIdentifier=win-x64 /p:PublishSingleFile=true
```

39) ReadyToRun publish

```bash
dotnet msbuild src/MyWeb/MyWeb.csproj /t:Publish /p:Configuration=Release /p:PublishReadyToRun=true
```

40) Trim publish (use with care)

```bash
dotnet msbuild src/MyWeb/MyWeb.csproj /t:Publish /p:Configuration=Release /p:PublishTrimmed=true
```

41) Single-file + trim (advanced)

```bash
dotnet msbuild src/MyWeb/MyWeb.csproj /t:Publish /p:Configuration=Release /p:RuntimeIdentifier=linux-x64 /p:PublishSingleFile=true /p:PublishTrimmed=true
```

42) Stamp environment property (pattern; app must use it)

```bash
dotnet msbuild src/MyWeb/MyWeb.csproj /t:Publish /p:Configuration=Release /p:EnvironmentName=Production
```

43) Publish with version stamping

```bash
dotnet msbuild src/MyWeb/MyWeb.csproj /t:Publish /p:Configuration=Release /p:Version=1.2.3
```

44) Publish with explicit TargetFramework (multi-TFM projects)

```bash
dotnet msbuild src/MyWeb/MyWeb.csproj /t:Publish /p:Configuration=Release /p:TargetFramework=net8.0
```

45) Publish with CI properties

```bash
dotnet msbuild src/MyWeb/MyWeb.csproj /t:Publish /p:Configuration=Release /p:ContinuousIntegrationBuild=true /p:Deterministic=true
```

46) Publish: RID + self-contained + output

```bash
dotnet msbuild src/MyWeb/MyWeb.csproj /t:Publish /p:Configuration=Release /p:RuntimeIdentifier=linux-x64 /p:SelfContained=true /p:PublishDir=artifacts/publish/linux-x64/
```

### D) Pack / NuGet / Versioning

47) Pack a library

```bash
dotnet msbuild src/MyLib/MyLib.csproj /t:Pack /p:Configuration=Release
```

48) Pack to a custom output path

```bash
dotnet msbuild src/MyLib/MyLib.csproj /t:Pack /p:Configuration=Release /p:PackageOutputPath=artifacts/nuget/
```

49) Pack with version

```bash
dotnet msbuild src/MyLib/MyLib.csproj /t:Pack /p:Configuration=Release /p:Version=1.2.3
```

50) Set AssemblyVersion / FileVersion

```bash
dotnet msbuild src/MyLib/MyLib.csproj /t:Build /p:Configuration=Release /p:AssemblyVersion=1.2.0.0 /p:FileVersion=1.2.3.0
```

51) InformationalVersion (commit metadata)

```bash
dotnet msbuild src/MyLib/MyLib.csproj /t:Build /p:Configuration=Release /p:InformationalVersion=1.2.3+sha.abcdef
```

52) Restore generating packages.lock.json

```bash
dotnet msbuild MySolution.sln /t:Restore /p:RestorePackagesWithLockFile=true
```

53) Restore locked mode (fail if lock changes)

```bash
dotnet msbuild MySolution.sln /t:Restore /p:RestoreLockedMode=true
```

54) Restore using a custom NuGet.config

```bash
dotnet msbuild MySolution.sln /t:Restore /p:RestoreConfigFile=NuGet.config
```

55) Restore with custom packages folder (CI cache)

```bash
dotnet msbuild MySolution.sln /t:Restore /p:RestorePackagesPath=artifacts/nuget-packages
```

### E) Diagnostics / Troubleshooting

56) Binary log (binlog) — best first step

```bash
dotnet msbuild MySolution.sln /t:Build /p:Configuration=Release /bl
```

57) Binlog with specific path

```bash
dotnet msbuild MySolution.sln /t:Build /p:Configuration=Release /bl:artifacts/logs/build.binlog
```

58) Verbosity: detailed

```bash
dotnet msbuild MySolution.sln /t:Build /v:detailed
```

59) Verbosity: diagnostic (only when needed)

```bash
dotnet msbuild MySolution.sln /t:Build /v:diag
```

60) File logger (text log)

```bash
dotnet msbuild MySolution.sln /t:Build /fl /flp:logfile=artifacts/logs/build.log;verbosity=normal
```

61) Console logger summary + performance

```bash
dotnet msbuild MySolution.sln /t:Build /clp:Summary;PerformanceSummary
```

62) Preprocess project (expanded after imports)

```bash
dotnet msbuild src/MyWeb/MyWeb.csproj /pp:artifacts/logs/preprocessed.xml
```

63) Graph build for solutions

```bash
dotnet msbuild MySolution.sln /t:Build /graphBuild /p:Configuration=Release
```

64) Run a single target explicitly (example: Clean)

```bash
dotnet msbuild src/MyWeb/MyWeb.csproj /t:Clean /p:Configuration=Release
```

65) Show command lines (helps reproduce compiler invocation)

```bash
dotnet msbuild MySolution.sln /t:Build /m /v:minimal /clp:ShowCommandLine
```

66) Disable node reuse (CI stability)

```bash
dotnet msbuild MySolution.sln /t:Build /nr:false /p:Configuration=Release
```

67) Limit parallelism

```bash
dotnet msbuild MySolution.sln /t:Build /m:4 /p:Configuration=Release
```

### F) Advanced build controls

68) Generic custom property pattern

```bash
dotnet msbuild src/MyWeb/MyWeb.csproj /t:Build /p:Configuration=Release /p:MyCustomProperty=Value
```

69) Override restore sources (quick feed test)

```bash
dotnet msbuild MySolution.sln /t:Restore /p:RestoreSources="https://api.nuget.org/v3/index.json;https://myfeed/v3/index.json"
```

70) Disable implicit restore (full control)

```bash
dotnet msbuild MySolution.sln /t:Build /p:Restore=false /p:BuildProjectReferences=true
```

71) Build without project references (debugging)

```bash
dotnet msbuild src/MyWeb/MyWeb.csproj /t:Build /p:BuildProjectReferences=false
```

72) Publish using apphost (common for exe-style hosting)

```bash
dotnet msbuild src/MyWeb/MyWeb.csproj /t:Publish /p:Configuration=Release /p:RuntimeIdentifier=linux-x64 /p:SelfContained=true /p:UseAppHost=true
```

73) Publish without apphost (edge cases)

```bash
dotnet msbuild src/MyWeb/MyWeb.csproj /t:Publish /p:Configuration=Release /p:UseAppHost=false
```

74) Restore with interactive auth (private feeds)

```bash
dotnet msbuild MySolution.sln /t:Restore /p:NuGetInteractive=true
```

75) Override MSBuild SDKs path (rare edge cases)

```bash
dotnet msbuild MySolution.sln /t:Build /p:MSBuildSDKsPath=/path/to/sdks
```

### G) msbuild.exe variants (Windows / VS Build Tools)

76) Build solution with msbuild.exe

```bash
msbuild MySolution.sln /t:Build /p:Configuration=Release /m
```

77) Restore with msbuild.exe

```bash
msbuild MySolution.sln /t:Restore
```

78) Publish with msbuild.exe

```bash
msbuild src\MyWeb\MyWeb.csproj /t:Publish /p:Configuration=Release /p:PublishDir=artifacts\publish\
```

79) Binlog with msbuild.exe

```bash
msbuild MySolution.sln /t:Build /p:Configuration=Release /bl:artifacts\logs\msbuild.binlog
```

80) Preprocess with msbuild.exe

```bash
msbuild src\MyWeb\MyWeb.csproj /pp:artifacts\logs\preprocessed.xml
```

* * *

## How to use this skill

When you describe a goal (e.g., “Publish linux-x64 self-contained single-file”), the skill should output:

- the **top 3** relevant commands from this list,
- the **few** MSBuild properties that matter most,
- and **one** diagnostic command (usually `/bl`) to capture a binlog if something fails.

## Caveats

- Trim/ReadyToRun/SingleFile can have app-specific implications.
- For build issues: rerun with `/bl` and inspect with MSBuild Structured Log Viewer.