package cmd

import (
	"fmt"
	"os"

	"canvas-cli/internal/api"
	"canvas-cli/internal/config"
	"canvas-cli/internal/ui"
)

var (
	jsonOutput bool
	perPage    int
	client     *api.Client
)

func Execute() {
	if len(os.Args) < 2 {
		printUsage()
		os.Exit(0)
	}

	// Parse global flags first
	args := os.Args[1:]
	var filteredArgs []string
	for i := 0; i < len(args); i++ {
		switch args[i] {
		case "--json":
			jsonOutput = true
		case "--per-page":
			if i+1 < len(args) {
				fmt.Sscanf(args[i+1], "%d", &perPage)
				i++
			}
		case "--help", "-h":
			printUsage()
			os.Exit(0)
		default:
			filteredArgs = append(filteredArgs, args[i])
		}
	}

	if perPage == 0 {
		perPage = 50
	}

	if len(filteredArgs) == 0 {
		printUsage()
		os.Exit(0)
	}

	command := filteredArgs[0]
	cmdArgs := filteredArgs[1:]

	// Commands that don't need auth
	switch command {
	case "configure":
		runConfigure()
		return
	case "help":
		printUsage()
		return
	case "version":
		fmt.Println("canvas-cli v1.0.0")
		return
	}

	// Load config and create API client
	cfg, err := config.Load()
	if err != nil {
		ui.Error(err.Error())
		os.Exit(1)
	}
	client = api.NewClient(cfg)
	client.PerPage = perPage

	// Route commands
	switch command {
	case "debug-login":
		runDebugLogin()
	case "whoami":
		runWhoami()
	case "courses":
		runCourses(cmdArgs)
	case "assignments":
		runAssignments(cmdArgs)
	case "grades":
		runGrades(cmdArgs)
	case "submissions":
		runSubmissions(cmdArgs)
	case "submit":
		runSubmit(cmdArgs)
	case "todo":
		runTodo()
	case "upcoming":
		runUpcoming()
	case "missing":
		runMissing()
	case "modules":
		runModules(cmdArgs)
	case "calendar":
		runCalendar(cmdArgs)
	case "discussions":
		runDiscussions(cmdArgs)
	case "announcements":
		runAnnouncements(cmdArgs)
	case "files":
		runFiles(cmdArgs)
	case "download":
		runDownload(cmdArgs)
	case "notifications":
		runNotifications()
	default:
		ui.Error(fmt.Sprintf("unknown command: %s", command))
		fmt.Println()
		printUsage()
		os.Exit(1)
	}
}

func printUsage() {
	fmt.Println(ui.C(ui.Bold+ui.Cyan, `
   ██████╗ █████╗ ███╗   ██╗██╗   ██╗ █████╗ ███████╗
  ██╔════╝██╔══██╗████╗  ██║██║   ██║██╔══██╗██╔════╝
  ██║     ███████║██╔██╗ ██║██║   ██║███████║███████╗
  ██║     ██╔══██║██║╚██╗██║╚██╗ ██╔╝██╔══██║╚════██║
  ╚██████╗██║  ██║██║ ╚████║ ╚████╔╝ ██║  ██║███████║
   ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝  ╚═══╝  ╚═╝  ╚═╝╚══════╝  CLI`))

	fmt.Println()
	fmt.Println(ui.C(ui.Bold, "  Canvas LMS command-line client"))
	fmt.Println()
	fmt.Println(ui.C(ui.Bold, "SETUP"))
	fmt.Println("  configure              Set up Canvas URL, username & password")
	fmt.Println("  whoami                 Show your profile info")
	fmt.Println()
	fmt.Println(ui.C(ui.Bold, "COURSES"))
	fmt.Println("  courses                List your active courses")
	fmt.Println("  courses <id>           Show course details")
	fmt.Println("  courses <id> users     List users in a course")
	fmt.Println()
	fmt.Println(ui.C(ui.Bold, "ASSIGNMENTS & GRADES"))
	fmt.Println("  assignments <course>             List assignments")
	fmt.Println("  assignments <course> <id>        Show assignment details")
	fmt.Println("  grades                           Grades overview (all courses)")
	fmt.Println("  grades <course>                  Grades for a course")
	fmt.Println("  submissions <course> <assign>    View your submission")
	fmt.Println("  submit <course> <assign> [opts]  Submit work")
	fmt.Println("    --text \"content\"               Submit text")
	fmt.Println("    --url <url>                    Submit a URL")
	fmt.Println()
	fmt.Println(ui.C(ui.Bold, "PRODUCTIVITY"))
	fmt.Println("  todo                   Pending to-do items")
	fmt.Println("  upcoming               Upcoming events & assignments")
	fmt.Println("  missing                Missing/late submissions")
	fmt.Println("  calendar               Upcoming calendar events")
	fmt.Println("    --start <date>       Start date (YYYY-MM-DD)")
	fmt.Println("    --end <date>         End date (YYYY-MM-DD)")
	fmt.Println()
	fmt.Println(ui.C(ui.Bold, "CONTENT"))
	fmt.Println("  modules <course>            List modules")
	fmt.Println("  modules <course> <id>       List module items")
	fmt.Println("  discussions <course>        List discussions")
	fmt.Println("  discussions <course> <id>   View discussion")
	fmt.Println("    --reply \"message\"         Post a reply")
	fmt.Println("  announcements               Recent announcements")
	fmt.Println("  announcements <course>      Course announcements")
	fmt.Println()
	fmt.Println(ui.C(ui.Bold, "FILES"))
	fmt.Println("  files <course>         List course files")
	fmt.Println("  download <file_id>     Download a file")
	fmt.Println("    -o <path>            Output path")
	fmt.Println()
	fmt.Println(ui.C(ui.Bold, "OTHER"))
	fmt.Println("  notifications          Activity stream")
	fmt.Println()
	fmt.Println(ui.C(ui.Bold, "FLAGS"))
	fmt.Println("  --json                 Output raw JSON")
	fmt.Println("  --per-page <n>         Results per page (default 50)")
	fmt.Println("  -h, --help             Show this help")
	fmt.Println()
}

func runConfigure() {
	_, err := config.RunSetup()
	if err != nil {
		ui.Error(err.Error())
		os.Exit(1)
	}
	ui.Success("Configuration complete!")
}
