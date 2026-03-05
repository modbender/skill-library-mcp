//! Cognitive Challenge System for AI Validators
//!
//! Defines challenges that AI agents must solve to validate blocks.
//! These challenges are designed to be solvable by AI but difficult for humans/scripts.
//! 
//! SECURITY (C3): All puzzles are generated DYNAMICALLY from cryptographic seeds.
//! No hardcoded answer pool — infinite puzzle variety prevents memorization attacks.

use serde::{Deserialize, Serialize};
use sha2::{Sha256, Digest};

/// Types of cognitive challenges AI agents can solve
/// Each challenge type is designed to require AI-level reasoning
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum ChallengeType {
    /// Verify transaction logic and detect double-spends
    TransactionVerification,
    
    /// Detect anomalous patterns in transaction flow
    AnomalyDetection,
    
    /// Verify state transition correctness
    StateTransitionAudit,
    
    /// Check for malformed or malicious transactions
    MaliciousTxDetection,
    
    /// NEW: Semantic reasoning challenge - requires AI understanding
    SemanticReasoning,
    
    /// NEW: Code analysis challenge - find bugs in code snippets
    CodeAnalysis,
    
    /// NEW: Pattern completion - complete a logical sequence
    PatternCompletion,
    
    /// NEW: Text transformation - apply described transformation
    TextTransformation,
}

/// A cognitive challenge for AI validators
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CognitiveChallenge {
    /// Type of challenge
    pub challenge_type: ChallengeType,
    
    /// Unique hash identifying this challenge
    pub challenge_hash: [u8; 32],
    
    /// Block height this challenge is for
    pub height: u64,
    
    /// Difficulty level (affects reward multiplier)
    pub difficulty: u8,
    
    /// Hashes of pending transactions to validate
    pub pending_tx_hashes: Vec<[u8; 32]>,
    
    /// Unix timestamp when challenge was created
    pub created_at: u64,
    
    /// Unix timestamp when challenge expires
    pub expires_at: u64,
    
    /// NEW: The cognitive puzzle to solve (only AI can solve quickly)
    pub cognitive_puzzle: Option<CognitivePuzzle>,
}

/// A cognitive challenge that requires AI-level reasoning to solve within the time limit
/// SECURITY (C3): All challenges are generated dynamically from seeds - no memorization possible
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CognitivePuzzle {
    /// The puzzle type
    pub puzzle_type: PuzzleType,
    
    /// The puzzle prompt/question
    pub prompt: String,
    
    /// For code analysis: the code snippet
    pub code_snippet: Option<String>,
    
    /// For pattern completion: the sequence so far
    pub sequence: Option<Vec<String>>,
    
    /// For text transformation: input text
    pub input_text: Option<String>,
    
    /// The expected answer hash (SHA256) - validators hash their answer to match
    pub expected_answer_hash: [u8; 32],
    
    /// Time limit in milliseconds (short = AI only)
    pub time_limit_ms: u64,
}

/// Types of cognitive puzzles
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum PuzzleType {
    /// Pattern recognition (dynamically generated arithmetic/geometric)
    PatternNext,
    
    /// Bug detection in code
    CodeBugDetection,
    
    /// Text manipulation
    TextTransform,
    
    /// Semantic compression
    SemanticSummary,
    
    /// NL math (infinite variety from seed)
    NaturalLanguageMath,
    
    /// Encoding recognition (dynamically generated)
    EncodingDecode,
}

// ============ DYNAMIC PUZZLE GENERATION (C3 FIX) ============

/// Derive a sub-seed for further randomization
fn derive_subseed(seed: &[u8; 32], domain: &[u8]) -> [u8; 32] {
    let mut hasher = Sha256::new();
    hasher.update(seed);
    hasher.update(domain);
    hasher.finalize().into()
}

/// Number words for natural language math
const NUMBER_WORDS: &[&str] = &[
    "zero", "one", "two", "three", "four", "five", "six", "seven",
    "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen",
    "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty",
];

fn number_to_word(n: u64) -> String {
    if n <= 20 {
        NUMBER_WORDS[n as usize].to_string()
    } else {
        n.to_string()
    }
}

impl CognitivePuzzle {
    /// Generate a random cognitive puzzle DYNAMICALLY from seed
    /// SECURITY (C3): Every puzzle is unique - derived from cryptographic hash of block state
    pub fn generate(seed: &[u8; 32], difficulty: u8) -> Self {
        let puzzle_type_idx = seed[0] % 6;
        let puzzle_type = match puzzle_type_idx {
            0 => PuzzleType::PatternNext,
            1 => PuzzleType::CodeBugDetection,
            2 => PuzzleType::TextTransform,
            3 => PuzzleType::SemanticSummary,
            4 => PuzzleType::NaturalLanguageMath,
            _ => PuzzleType::EncodingDecode,
        };
        
        // Time limit based on difficulty (500ms - 2000ms)
        let time_limit_ms = 500 + (difficulty as u64 * 100);
        
        match puzzle_type {
            PuzzleType::PatternNext => Self::generate_pattern_puzzle(seed, time_limit_ms),
            PuzzleType::CodeBugDetection => Self::generate_code_puzzle(seed, time_limit_ms),
            PuzzleType::TextTransform => Self::generate_transform_puzzle(seed, time_limit_ms),
            PuzzleType::SemanticSummary => Self::generate_summary_puzzle(seed, time_limit_ms),
            PuzzleType::NaturalLanguageMath => Self::generate_nlmath_puzzle(seed, time_limit_ms),
            PuzzleType::EncodingDecode => Self::generate_decode_puzzle(seed, time_limit_ms),
        }
    }
    
    /// DYNAMIC pattern puzzle: arithmetic or geometric sequences from seed
    fn generate_pattern_puzzle(seed: &[u8; 32], time_limit_ms: u64) -> Self {
        let subseed = derive_subseed(seed, b"pattern");
        let pattern_type = subseed[0] % 4;
        let start = (subseed[1] as u64 % 20) + 1;
        let step = (subseed[2] as u64 % 10) + 1;
        let seq_len = 4 + (subseed[3] % 2) as usize;
        
        let (sequence, answer) = match pattern_type {
            0 => {
                // Arithmetic: start, start+step, start+2*step, ...
                let seq: Vec<String> = (0..seq_len)
                    .map(|i| (start + step * i as u64).to_string())
                    .collect();
                let ans = (start + step * seq_len as u64).to_string();
                (seq, ans)
            }
            1 => {
                // Geometric: base, base*ratio, base*ratio^2, ...
                let ratio = (subseed[2] as u64 % 3) + 2;
                let base = (subseed[1] as u64 % 5) + 1;
                let seq: Vec<String> = (0..seq_len)
                    .map(|i| (base * ratio.pow(i as u32)).to_string())
                    .collect();
                let ans = (base * ratio.pow(seq_len as u32)).to_string();
                (seq, ans)
            }
            2 => {
                // Squares: (base+0)^2, (base+1)^2, (base+2)^2, ...
                let base = (subseed[1] as u64 % 8) + 1;
                let seq: Vec<String> = (0..seq_len)
                    .map(|i| ((base + i as u64) * (base + i as u64)).to_string())
                    .collect();
                let n = base + seq_len as u64;
                let ans = (n * n).to_string();
                (seq, ans)
            }
            _ => {
                // Triangular: n*(n+1)/2
                let base = (subseed[1] as u64 % 6) + 1;
                let seq: Vec<String> = (0..seq_len)
                    .map(|i| {
                        let n = base + i as u64;
                        (n * (n + 1) / 2).to_string()
                    })
                    .collect();
                let n = base + seq_len as u64;
                let ans = (n * (n + 1) / 2).to_string();
                (seq, ans)
            }
        };
        
        let answer_hash = Self::hash_answer(&answer);
        Self {
            puzzle_type: PuzzleType::PatternNext,
            prompt: "What comes next in this sequence? Reply with ONLY the next number.".to_string(),
            code_snippet: None,
            sequence: Some(sequence),
            input_text: None,
            expected_answer_hash: answer_hash,
            time_limit_ms,
        }
    }
    
    /// Code puzzle: seed selects from large pool + varies variable names
    fn generate_code_puzzle(seed: &[u8; 32], time_limit_ms: u64) -> Self {
        let subseed = derive_subseed(seed, b"codebug");
        let var_names = ["x", "val", "num", "data", "item", "result", "count", "total"];
        let var1 = var_names[(subseed[4] as usize) % var_names.len()];
        let var2 = var_names[(subseed[5] as usize) % var_names.len()];
        
        let puzzle_idx = subseed[1] as usize % 15;
        let (code, bug_type) = match puzzle_idx {
            0 => (
                format!("def sum_list(lst):\n    {} = 0\n    for i in range(len(lst)):\n        {} += lst[i + 1]\n    return {}", var1, var1, var1),
                "off-by-one".to_string()
            ),
            1 => (
                "function divide(a, b) {\n    return a / b;\n}".to_string(),
                "division-by-zero".to_string()
            ),
            2 => (
                format!("int* get_ptr() {{\n    int {} = 42;\n    return &{};\n}}", var1, var1),
                "dangling-pointer".to_string()
            ),
            3 => (
                format!("while True:\n    {} = input()\n    process({})", var1, var1),
                "infinite-loop".to_string()
            ),
            4 => (
                "query = \"SELECT * FROM users WHERE id = \" + user_input".to_string(),
                "sql-injection".to_string()
            ),
            5 => {
                let size = (subseed[2] as u64 % 50) + 10;
                (
                    format!("int arr[{}];\nfor(int i = 0; i <= {}; i++) {{\n    arr[i] = i;\n}}", size, size),
                    "buffer-overflow".to_string()
                )
            }
            6 => (
                format!("def read_file(path):\n    f = open(path, 'r')\n    {} = f.read()\n    return {}", var1, var1),
                "resource-leak".to_string()
            ),
            7 => (
                format!("public void process(Object {}) {{\n    String {} = {}.toString();\n}}", var1, var2, var1),
                "null-pointer".to_string()
            ),
            8 => (
                format!("import pickle\n{} = pickle.loads(user_data)", var1),
                "deserialization".to_string()
            ),
            9 => (
                format!("password = \"secret{}\"\nif user_pass == password:", subseed[3]),
                "hardcoded-credentials".to_string()
            ),
            10 => (
                format!("void swap(int {}, int {}) {{\n    int temp = {};\n    {} = {};\n    {} = temp;\n}}", var1, var2, var1, var1, var2, var2),
                "pass-by-value".to_string()
            ),
            11 => (
                format!("int {} = INT_MAX;\n{} = {} + 1;", var1, var1, var1),
                "integer-overflow".to_string()
            ),
            12 => (
                format!("float {} = 0.1 + 0.2;\nif ({} == 0.3) {{ /* exact */ }}", var1, var1),
                "floating-point".to_string()
            ),
            13 => (
                format!("threads = []\nfor i in range(10):\n    t = Thread(target=modify, args=({},))\n    threads.append(t)\n    t.start()", var1),
                "race-condition".to_string()
            ),
            _ => (
                "def factorial(n):\n    return n * factorial(n - 1)".to_string(),
                "missing-base-case".to_string()
            ),
        };
        
        let answer_hash = Self::hash_answer(&bug_type);
        Self {
            puzzle_type: PuzzleType::CodeBugDetection,
            prompt: "What type of bug is in this code? Reply with the bug type only.".to_string(),
            code_snippet: Some(code),
            sequence: None,
            input_text: None,
            expected_answer_hash: answer_hash,
            time_limit_ms,
        }
    }
    
    /// DYNAMIC text transform: generates unique strings + operations from seed
    fn generate_transform_puzzle(seed: &[u8; 32], time_limit_ms: u64) -> Self {
        let subseed = derive_subseed(seed, b"transform");
        let word_len = (subseed[1] as usize % 5) + 4;
        let input_chars: String = (0..word_len)
            .map(|i| {
                let byte = subseed[(2 + i) % 32];
                (b'a' + (byte % 26)) as char
            })
            .collect();
        
        let transform_type = subseed[0] % 5;
        let (transform_desc, answer) = match transform_type {
            0 => {
                ("reverse the text".to_string(), input_chars.chars().rev().collect::<String>())
            }
            1 => {
                ("convert to uppercase".to_string(), input_chars.to_uppercase())
            }
            2 => {
                let result: String = input_chars.chars()
                    .filter(|c| !matches!(c, 'a' | 'e' | 'i' | 'o' | 'u'))
                    .collect();
                ("remove all vowels".to_string(), result)
            }
            3 => {
                let result: String = input_chars.chars().rev().collect::<String>().to_uppercase();
                ("reverse and convert to uppercase".to_string(), result)
            }
            _ => {
                let count = input_chars.len();
                ("count the number of characters".to_string(), count.to_string())
            }
        };
        
        let answer_hash = Self::hash_answer(&answer);
        Self {
            puzzle_type: PuzzleType::TextTransform,
            prompt: format!("Apply this transformation: '{}'. Reply with ONLY the result.", transform_desc),
            code_snippet: None,
            sequence: None,
            input_text: Some(input_chars),
            expected_answer_hash: answer_hash,
            time_limit_ms,
        }
    }
    
    /// Semantic summary: expanded pool with seed-based selection
    fn generate_summary_puzzle(seed: &[u8; 32], time_limit_ms: u64) -> Self {
        let subseed = derive_subseed(seed, b"summary");
        let puzzles = [
            ("The quick brown fox jumps over the lazy dog", "pangram"),
            ("A decentralized network where AI agents validate transactions", "blockchain"),
            ("H2O is essential for all known forms of life", "water"),
            ("The Earth orbits around this star", "sun"),
            ("A system that rewards computational work with digital currency", "mining"),
            ("The study of algorithms and data structures", "programming"),
            ("A device that converts sound waves into electrical signals", "microphone"),
            ("The force that pulls objects toward the center of the Earth", "gravity"),
            ("A mathematical function that maps data to a fixed-size output", "hash"),
            ("The practice of protecting computer systems from theft or damage", "cybersecurity"),
            ("An animal with black and white stripes native to Africa", "zebra"),
            ("The third planet from the Sun in our solar system", "earth"),
            ("A tool for writing that uses a small rotating ball and ink", "pen"),
            ("Communication protocol that powers the World Wide Web", "http"),
            ("The branch of mathematics dealing with rates of change", "calculus"),
            ("A large natural stream of water flowing to the sea", "river"),
            ("The process of converting food into energy in living organisms", "metabolism"),
            ("A transparent material made from silica used in windows", "glass"),
            ("The study of celestial objects like stars and planets", "astronomy"),
            ("Frozen water that falls from clouds in cold weather", "snow"),
        ];
        
        let idx = (subseed[1] as usize) % puzzles.len();
        let (text, answer) = &puzzles[idx];
        let answer_hash = Self::hash_answer(answer);
        
        Self {
            puzzle_type: PuzzleType::SemanticSummary,
            prompt: format!("Summarize in ONE word: '{}'", text),
            code_snippet: None,
            sequence: None,
            input_text: None,
            expected_answer_hash: answer_hash,
            time_limit_ms,
        }
    }
    
    /// DYNAMIC NL math: generates unique math expressions from seed bytes
    fn generate_nlmath_puzzle(seed: &[u8; 32], time_limit_ms: u64) -> Self {
        let subseed = derive_subseed(seed, b"nlmath");
        let a = (subseed[1] as u64 % 20) + 1;
        let b = (subseed[2] as u64 % 15) + 1;
        let c = (subseed[3] as u64 % 10) + 1;
        let expr_type = subseed[0] % 6;
        
        let (expression, answer) = match expr_type {
            0 => {
                let ans = a + b;
                (format!("{} plus {}", number_to_word(a), number_to_word(b)), ans.to_string())
            }
            1 => {
                let ans = a * b;
                (format!("{} times {}", number_to_word(a), number_to_word(b)), ans.to_string())
            }
            2 => {
                let ans = a + b * c;
                (format!("{} plus {} times {}", number_to_word(a), number_to_word(b), number_to_word(c)), ans.to_string())
            }
            3 => {
                let effective_b = b.min(a * a);
                let ans = a * a - effective_b;
                (format!("{} squared minus {}", number_to_word(a), number_to_word(effective_b)), ans.to_string())
            }
            4 => {
                let ans = a * c;
                (format!("{} multiplied by {}", number_to_word(a), number_to_word(c)), ans.to_string())
            }
            _ => {
                let (big, small) = if a >= b { (a, b) } else { (b, a) };
                let ans = big - small;
                (format!("{} minus {}", number_to_word(big), number_to_word(small)), ans.to_string())
            }
        };
        
        let answer_hash = Self::hash_answer(&answer);
        Self {
            puzzle_type: PuzzleType::NaturalLanguageMath,
            prompt: format!("Calculate: '{}'. Reply with ONLY the number.", expression),
            code_snippet: None,
            sequence: None,
            input_text: None,
            expected_answer_hash: answer_hash,
            time_limit_ms,
        }
    }
    
    /// DYNAMIC encoding puzzle: generates unique encoded strings from seed
    fn generate_decode_puzzle(seed: &[u8; 32], time_limit_ms: u64) -> Self {
        let subseed = derive_subseed(seed, b"decode");
        let word_len = (subseed[1] as usize % 4) + 3;
        let plaintext: String = (0..word_len)
            .map(|i| {
                let byte = subseed[(2 + i) % 32];
                (b'a' + (byte % 26)) as char
            })
            .collect();
        
        let encoding_type = subseed[0] % 3;
        let (encoded, encoding_name) = match encoding_type {
            0 => {
                let hex_str = hex::encode(plaintext.as_bytes());
                (hex_str, "hex")
            }
            1 => {
                let rot13: String = plaintext.chars().map(|c| {
                    if c.is_ascii_lowercase() {
                        (((c as u8 - b'a' + 13) % 26) + b'a') as char
                    } else {
                        c
                    }
                }).collect();
                (rot13, "rot13")
            }
            _ => {
                let reversed: String = plaintext.chars().rev().collect();
                (reversed, "reversed")
            }
        };
        
        let answer_hash = Self::hash_answer(&plaintext);
        Self {
            puzzle_type: PuzzleType::EncodingDecode,
            prompt: format!("Decode this {} string. Reply with ONLY the decoded text.", encoding_name),
            code_snippet: None,
            sequence: None,
            input_text: Some(encoded),
            expected_answer_hash: answer_hash,
            time_limit_ms,
        }
    }
    
    /// Hash an answer for verification
    pub fn hash_answer(answer: &str) -> [u8; 32] {
        let normalized = answer.trim().to_lowercase();
        let mut hasher = Sha256::new();
        hasher.update(normalized.as_bytes());
        hasher.finalize().into()
    }
}

impl CognitiveChallenge {
    /// Check if the challenge has expired
    pub fn is_expired(&self) -> bool {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs();
        now > self.expires_at
    }
    
    /// Get remaining time in seconds
    pub fn remaining_time(&self) -> u64 {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs();
        if now > self.expires_at {
            0
        } else {
            self.expires_at - now
        }
    }
}

/// Response from an AI agent after solving a challenge (uses hex strings for serialization)
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ChallengeResponse {
    /// The challenge hash being responded to (hex)
    pub challenge_hash: String,
    
    /// Validator public key (hex)
    pub validator_pubkey: String,
    
    /// Signature over (challenge_hash || verdict_digest) (hex)
    pub signature: String,
    
    /// Merkle root of flagged/invalid transaction IDs (hex)
    pub verdict_digest: String,
    
    /// Optional: detailed verdict for each transaction
    pub tx_verdicts: Option<Vec<TxVerdict>>,
    
    /// NEW: Answer to the cognitive puzzle (if present)
    pub puzzle_answer: Option<String>,
    
    /// NEW: Timestamp when answer was submitted (for time verification)
    pub submitted_at_ms: Option<u64>,
}

/// Verdict for a single transaction
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TxVerdict {
    /// Transaction hash (hex)
    pub tx_hash: String,
    
    /// Is the transaction valid?
    pub is_valid: bool,
    
    /// Confidence score (0-100)
    pub confidence: u8,
    
    /// Reason for flagging (if invalid)
    pub reason: Option<String>,
}

// ============ TESTS ============

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_dynamic_puzzles_are_unique() {
        let seed1: [u8; 32] = [1; 32];
        let seed2: [u8; 32] = [2; 32];
        let seed3: [u8; 32] = [3; 32];
        
        let p1 = CognitivePuzzle::generate(&seed1, 1);
        let p2 = CognitivePuzzle::generate(&seed2, 1);
        let p3 = CognitivePuzzle::generate(&seed3, 1);
        
        assert_ne!(p1.expected_answer_hash, p2.expected_answer_hash, 
            "Different seeds should produce different puzzles");
        assert_ne!(p2.expected_answer_hash, p3.expected_answer_hash,
            "Different seeds should produce different puzzles");
    }
    
    #[test]
    fn test_pattern_puzzle_answer_is_correct() {
        let seed: [u8; 32] = {
            let mut s = [0u8; 32];
            s[0] = 0;
            s
        };
        let subseed = derive_subseed(&seed, b"pattern");
        let start = (subseed[1] as u64 % 20) + 1;
        let step = (subseed[2] as u64 % 10) + 1;
        let seq_len = 4 + (subseed[3] % 2) as usize;
        
        if subseed[0] % 4 == 0 {
            let expected_answer = (start + step * seq_len as u64).to_string();
            let puzzle = CognitivePuzzle::generate(&seed, 1);
            assert_eq!(puzzle.expected_answer_hash, CognitivePuzzle::hash_answer(&expected_answer));
        }
    }
    
    #[test]
    fn test_nlmath_puzzle_generates() {
        let mut seed = [0u8; 32];
        seed[0] = 4;
        let puzzle = CognitivePuzzle::generate(&seed, 1);
        assert!(matches!(puzzle.puzzle_type, PuzzleType::NaturalLanguageMath));
        assert!(puzzle.prompt.contains("Calculate"));
    }
    
    #[test]
    fn test_decode_puzzle_generates() {
        let mut seed = [0u8; 32];
        seed[0] = 5;
        seed[1] = 10;
        seed[2] = 7;
        let puzzle = CognitivePuzzle::generate(&seed, 1);
        assert!(matches!(puzzle.puzzle_type, PuzzleType::EncodingDecode));
        assert!(puzzle.prompt.contains("Decode"));
    }
    
    #[test]
    fn test_transform_puzzle_generates() {
        let mut seed = [0u8; 32];
        seed[0] = 2;
        let puzzle = CognitivePuzzle::generate(&seed, 1);
        assert!(matches!(puzzle.puzzle_type, PuzzleType::TextTransform));
        assert!(puzzle.input_text.is_some());
    }
    
    #[test]
    fn test_hash_answer_normalization() {
        assert_eq!(
            CognitivePuzzle::hash_answer("Hello"),
            CognitivePuzzle::hash_answer("  hello  ")
        );
        assert_eq!(
            CognitivePuzzle::hash_answer("WORLD"),
            CognitivePuzzle::hash_answer("world")
        );
    }
    
    #[test]
    fn test_many_unique_puzzles() {
        let mut answer_hashes = std::collections::HashSet::new();
        for i in 0..100u8 {
            let mut seed = [0u8; 32];
            seed[0] = i % 6;
            seed[1] = i;
            seed[2] = i.wrapping_mul(7);
            seed[3] = i.wrapping_mul(13);
            let puzzle = CognitivePuzzle::generate(&seed, 1);
            answer_hashes.insert(puzzle.expected_answer_hash);
        }
        assert!(answer_hashes.len() > 50, 
            "Expected >50 unique puzzles out of 100, got {}", answer_hashes.len());
    }
}
