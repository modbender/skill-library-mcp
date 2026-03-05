using UnityEngine;
using UnityEditor;

namespace LevelDesignTools
{
    /// <summary>
    /// Player controller setup tools
    /// Creates FPS, Third-Person, and Top-Down controllers
    /// </summary>
    public static class PlayerSetup
    {
        [MenuItem("Level Design/Player/Create FPS Controller")]
        public static GameObject CreateFPSPlayer()
        {
            // Remove existing player
            var existing = GameObject.FindWithTag("Player");
            if (existing != null)
                Object.DestroyImmediate(existing);
            
            // Create player container
            var player = new GameObject("Player");
            player.tag = "Player";
            player.transform.position = new Vector3(0, 2, 0);
            
            // Character controller
            var cc = player.AddComponent<CharacterController>();
            cc.height = 2f;
            cc.radius = 0.5f;
            cc.center = Vector3.zero;
            cc.stepOffset = 0.3f;
            
            // Camera
            var camGO = new GameObject("PlayerCamera");
            camGO.transform.SetParent(player.transform);
            camGO.transform.localPosition = new Vector3(0, 0.8f, 0);
            
            var cam = camGO.AddComponent<Camera>();
            cam.tag = "MainCamera";
            cam.nearClipPlane = 0.01f;
            
            // Add basic controller script
            var controller = player.AddComponent<BasicFPSController>();
            controller.cameraTransform = camGO.transform;
            
            // Add ground check
            var groundCheckGO = new GameObject("GroundCheck");
            groundCheckGO.transform.SetParent(player.transform);
            groundCheckGO.transform.localPosition = new Vector3(0, -0.9f, 0);
            controller.groundCheck = groundCheckGO.transform;
            
            Debug.Log("FPS Player created");
            return player;
        }

        [MenuItem("Level Design/Player/Create Third-Person Controller")]
        public static GameObject CreateThirdPersonPlayer()
        {
            // Remove existing player
            var existing = GameObject.FindWithTag("Player");
            if (existing != null)
                Object.DestroyImmediate(existing);
            
            // Create player
            var player = new GameObject("Player");
            player.tag = "Player";
            player.transform.position = new Vector3(0, 2, 0);
            
            // Character controller
            var cc = player.AddComponent<CharacterController>();
            cc.height = 2f;
            cc.radius = 0.5f;
            cc.center = Vector3.zero;
            
            // Add a simple capsule mesh for visualization
            var visualGO = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            visualGO.name = "Visuals";
            visualGO.transform.SetParent(player.transform);
            visualGO.transform.localPosition = Vector3.zero;
            Object.DestroyImmediate(visualGO.GetComponent<CapsuleCollider>());
            
            // Camera rig
            var camRig = new GameObject("CameraRig");
            var cam = camRig.AddComponent<Camera>();
            cam.tag = "MainCamera";
            cam.transform.position = new Vector3(0, 3, -5);
            cam.transform.LookAt(player.transform);
            
            // Add controller
            var controller = player.AddComponent<BasicThirdPersonController>();
            controller.cameraTransform = camRig.transform;
            
            Debug.Log("Third-Person Player created");
            return player;
        }

        [MenuItem("Level Design/Player/Create Top-Down Controller")]
        public static GameObject CreateTopDownPlayer()
        {
            // Remove existing player
            var existing = GameObject.FindWithTag("Player");
            if (existing != null)
                Object.DestroyImmediate(existing);
            
            // Create player
            var player = new GameObject("Player");
            player.tag = "Player";
            player.transform.position = new Vector3(0, 0.5f, 0);
            
            // Capsule collider
            var col = player.AddComponent<CapsuleCollider>();
            col.height = 1f;
            col.radius = 0.5f;
            col.center = Vector3.zero;
            
            // Rigidbody for physics-based movement
            var rb = player.AddComponent<Rigidbody>();
            rb.freezeRotation = true;
            
            // Visual
            var visualGO = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            visualGO.name = "Visuals";
            visualGO.transform.SetParent(player.transform);
            visualGO.transform.localPosition = Vector3.zero;
            visualGO.transform.localScale = new Vector3(1f, 0.5f, 1f);
            Object.DestroyImmediate(visualGO.GetComponent<CapsuleCollider>());
            
            // Top-down camera
            var camRig = new GameObject("TopDownCamera");
            var cam = camRig.AddComponent<Camera>();
            cam.tag = "MainCamera";
            cam.orthographic = true;
            cam.orthographicSize = 10f;
            cam.transform.position = new Vector3(0, 15, 0);
            cam.transform.rotation = Quaternion.Euler(90, 0, 0);
            
            // Add controller
            var controller = player.AddComponent<BasicTopDownController>();
            controller.cameraTransform = camRig.transform;
            
            Debug.Log("Top-Down Player created");
            return player;
        }
    }

    /// <summary>
    /// Basic FPS controller component
    /// </summary>
    public class BasicFPSController : MonoBehaviour
    {
        [Header("Movement")]
        public float walkSpeed = 5f;
        public float sprintSpeed = 8f;
        public float jumpForce = 8f;
        public float gravity = -20f;
        
        [Header("Look")]
        public Transform cameraTransform;
        public float mouseSensitivity = 2f;
        public float lookXLimit = 90f;
        
        [Header("Ground Check")]
        public Transform groundCheck;
        public float groundDistance = 0.4f;
        public LayerMask groundMask;
        
        private CharacterController controller;
        private Vector3 velocity;
        private float xRotation = 0f;
        private bool isGrounded;
        
        void Start()
        {
            controller = GetComponent<CharacterController>();
            Cursor.lockState = CursorLockMode.Locked;
        }
        
        void Update()
        {
            // Ground check
            isGrounded = Physics.CheckSphere(groundCheck.position, groundDistance, groundMask);
            if (isGrounded && velocity.y < 0)
                velocity.y = -2f;
            
            // Look
            float mouseX = Input.GetAxis("Mouse X") * mouseSensitivity;
            float mouseY = Input.GetAxis("Mouse Y") * mouseSensitivity;
            
            xRotation -= mouseY;
            xRotation = Mathf.Clamp(xRotation, -lookXLimit, lookXLimit);
            
            cameraTransform.localRotation = Quaternion.Euler(xRotation, 0f, 0f);
            transform.Rotate(Vector3.up * mouseX);
            
            // Move
            float speed = Input.GetKey(KeyCode.LeftShift) ? sprintSpeed : walkSpeed;
            float x = Input.GetAxis("Horizontal");
            float z = Input.GetAxis("Vertical");
            
            Vector3 move = transform.right * x + transform.forward * z;
            controller.Move(move * speed * Time.deltaTime);
            
            // Jump
            if (Input.GetButtonDown("Jump") && isGrounded)
                velocity.y = jumpForce;
            
            // Gravity
            velocity.y += gravity * Time.deltaTime;
            controller.Move(velocity * Time.deltaTime);
        }
    }

    /// <summary>
    /// Basic third-person controller component
    /// </summary>
    public class BasicThirdPersonController : MonoBehaviour
    {
        [Header("Movement")]
        public float moveSpeed = 5f;
        public float rotationSpeed = 10f;
        
        [Header("Camera")]
        public Transform cameraTransform;
        public float cameraDistance = 5f;
        public float cameraHeight = 2f;
        
        private CharacterController controller;
        
        void Start()
        {
            controller = GetComponent<CharacterController>();
        }
        
        void Update()
        {
            // Get input
            float horizontal = Input.GetAxis("Horizontal");
            float vertical = Input.GetAxis("Vertical");
            
            Vector3 direction = new Vector3(horizontal, 0, vertical).normalized;
            
            if (direction.magnitude >= 0.1f)
            {
                // Rotate towards movement direction
                float targetAngle = Mathf.Atan2(direction.x, direction.z) * Mathf.Rad2Deg;
                float angle = Mathf.SmoothDampAngle(transform.eulerAngles.y, targetAngle, 
                    ref rotationSpeed, 0.1f);
                transform.rotation = Quaternion.Euler(0f, angle, 0f);
                
                // Move
                Vector3 moveDir = Quaternion.Euler(0f, targetAngle, 0f) * Vector3.forward;
                controller.Move(moveDir.normalized * moveSpeed * Time.deltaTime);
            }
            
            // Update camera position
            if (cameraTransform != null)
            {
                Vector3 targetPos = transform.position - transform.forward * cameraDistance;
                targetPos.y += cameraHeight;
                cameraTransform.position = Vector3.Lerp(cameraTransform.position, targetPos, Time.deltaTime * 5f);
                cameraTransform.LookAt(transform.position + Vector3.up);
            }
        }
    }

    /// <summary>
    /// Basic top-down controller component
    /// </summary>
    public class BasicTopDownController : MonoBehaviour
    {
        [Header("Movement")]
        public float moveSpeed = 8f;
        
        [Header("Camera")]
        public Transform cameraTransform;
        
        private Rigidbody rb;
        
        void Start()
        {
            rb = GetComponent<Rigidbody>();
        }
        
        void FixedUpdate()
        {
            float horizontal = Input.GetAxis("Horizontal");
            float vertical = Input.GetAxis("Vertical");
            
            Vector3 movement = new Vector3(horizontal, 0, vertical);
            rb.velocity = movement * moveSpeed;
            
            // Update camera to follow
            if (cameraTransform != null)
            {
                Vector3 targetPos = transform.position + Vector3.up * 15f;
                cameraTransform.position = Vector3.Lerp(cameraTransform.position, targetPos, Time.fixedDeltaTime * 5f);
            }
        }
    }
}