# Performance Optimization Guide

## Understanding Laziness

### When Laziness Helps
```haskell
-- Infinite structures work naturally
fibonacci :: [Integer]
fibonacci = 0 : 1 : zipWith (+) fibonacci (tail fibonacci)

-- Take only what you need
first10Fibs :: [Integer]
first10Fibs = take 10 fibonacci

-- Short-circuiting evaluation
any' :: (a -> Bool) -> [a] -> Bool
any' p = foldr (\x acc -> p x || acc) False  -- Stops at first True

-- Efficient stream fusion
processLargeList :: [Int] -> Int
processLargeList = sum . filter even . map (*2)  -- Fuses into single pass
```

### When Laziness Hurts
```haskell
-- Space leak: accumulating thunks
badSum :: [Int] -> Int
badSum = foldl (+) 0  -- Builds up thunk chain

-- Good: strict evaluation
goodSum :: [Int] -> Int  
goodSum = foldl' (+) 0  -- Forces evaluation at each step

-- Lazy fields cause space leaks
data BadCounter = BadCounter 
  { count :: Int      -- Lazy field accumulates thunks
  , name :: String 
  }

-- Better: strict fields
data GoodCounter = GoodCounter
  { count :: !Int     -- Strict field
  , name :: !String   -- Forces evaluation
  }
```

## Strictness Annotations

### Bang Patterns
```haskell
{-# LANGUAGE BangPatterns #-}

-- Force evaluation of parameters
strictMap :: (a -> b) -> [a] -> [b]
strictMap _ [] = []
strictMap f (!x:xs) = f x : strictMap f xs  -- x evaluated immediately

-- Strict local bindings
processData :: [Int] -> Int
processData xs = 
  let !len = length xs      -- Evaluated immediately
      !avg = sum xs `div` len
  in avg * 2

-- Strict pattern matching in case
parseNumber :: String -> Maybe Int
parseNumber s = case readMaybe s of
  !result@(Just _) -> result  -- Force evaluation of successful parse
  Nothing -> Nothing
```

### UNPACK Pragma
```haskell
-- Unpack small strict fields directly into constructor
data Point = Point 
  { pointX :: {-# UNPACK #-} !Double  -- No pointer indirection
  , pointY :: {-# UNPACK #-} !Double
  } deriving (Show, Eq)

-- Automatic unpacking for simple types  
data RGB = RGB 
  { red :: {-# UNPACK #-} !Word8
  , green :: {-# UNPACK #-} !Word8  
  , blue :: {-# UNPACK #-} !Word8
  }

-- Don't unpack large or complex types
data User = User
  { userId :: {-# UNPACK #-} !Int     -- Good: small, simple
  , userName :: !Text                 -- Don't unpack: Text is complex
  , userTags :: [Tag]                 -- Don't unpack: list is lazy by design
  }
```

### Seq and DeepSeq
```haskell
import Control.DeepSeq

-- seq: evaluate to weak head normal form (WHNF)
forceHead :: [a] -> [a]
forceHead xs = length xs `seq` xs  -- Forces spine evaluation

-- deepseq: fully evaluate structure  
forceAll :: NFData a => [a] -> [a]
forceAll xs = rnf xs `seq` xs  -- Forces complete evaluation

-- Custom NFData instances
instance NFData User where
  rnf User{..} = rnf userId `seq` 
                 rnf userName `seq` 
                 rnf userEmail

-- Parallel strategies with evaluation control
import Control.Parallel.Strategies

parallelMap :: NFData b => (a -> b) -> [a] -> [b]
parallelMap f xs = map f xs `using` parList rdeepseq
```

## Memory Profiling

### Heap Profiling Setup
```bash
# Build with profiling enabled
cabal build --enable-profiling

# Generate heap profile
./myapp +RTS -h -p

# Different heap profiling modes
./myapp +RTS -hc     # Cost center profiling
./myapp +RTS -hm     # Module profiling
./myapp +RTS -hy     # Type profiling
./myapp +RTS -hd     # Closure description profiling

# Generate visual heap profile
hp2ps -c myapp.hp    # Creates myapp.ps
```

### Cost Centers
```haskell
{-# OPTIONS_GHC -fprof-auto #-}  -- Automatic cost centers

-- Manual cost centers for precision
expensiveComputation :: [Int] -> Int
expensiveComputation xs = {-# SCC "expensive_computation" #-}
  sum $ map complexFunction xs
  where
    complexFunction x = {-# SCC "complex_function" #-}
      x * x + fibonacci x

-- Time profiling
main :: IO ()
main = do
  let result = {-# SCC "main_computation" #-} 
               expensiveComputation [1..10000]
  print result
```

### Space Leak Detection
```haskell
-- Common space leak patterns

-- 1. Lazy accumulator
badFoldl :: [Int] -> Int
badFoldl = foldl (+) 0  -- Creates thunk chain

-- Fix: strict accumulator
goodFoldl :: [Int] -> Int  
goodFoldl = foldl' (+) 0

-- 2. Retaining large structures
processFile :: FilePath -> IO Int
processFile file = do
  content <- readFile file  -- Entire file in memory
  -- Process content...
  return (length content)   -- File content retained until return

-- Fix: streaming or strict reading
processFileStrict :: FilePath -> IO Int  
processFileStrict file = do
  content <- readFile file
  let !len = length content  -- Force evaluation
  return len

-- 3. Monadic accumulation
badMonadicSum :: [IO Int] -> IO Int
badMonadicSum [] = return 0
badMonadicSum (x:xs) = do
  val <- x
  rest <- badMonadicSum xs
  return (val + rest)  -- Accumulates thunks in IO

-- Fix: strict evaluation in monad
goodMonadicSum :: [IO Int] -> IO Int
goodMonadicSum = foldM (\acc action -> do
  val <- action
  let !newAcc = acc + val
  return newAcc) 0
```

## High-Performance Data Structures

### Vector for Arrays
```haskell
import qualified Data.Vector as V
import qualified Data.Vector.Unboxed as U
import qualified Data.Vector.Storable as S
import qualified Data.Vector.Mutable as MV

-- Choose the right vector type
-- V.Vector: Boxed vectors for complex types  
-- U.Vector: Unboxed vectors for primitives (faster)
-- S.Vector: Storable vectors for C interop

-- Efficient array processing
processNumbers :: U.Vector Double -> Double
processNumbers numbers = 
  U.sum $ U.map (\x -> x * x + 1) $ U.filter (> 0) numbers

-- In-place mutation for performance
createLookupTable :: Int -> IO (U.Vector Int)
createLookupTable size = do
  mv <- MV.new size
  forM_ [0..size-1] $ \i -> 
    MV.write mv i (expensiveFunction i)
  U.freeze mv

-- Parallel vector operations
import qualified Data.Vector.Parallel as PV

parallelProcessing :: U.Vector Double -> U.Vector Double
parallelProcessing = PV.map expensiveFunction
```

### ByteString for Binary Data
```haskell
import qualified Data.ByteString as BS
import qualified Data.ByteString.Lazy as LBS
import qualified Data.ByteString.Builder as B

-- Efficient string building
buildLargeByteString :: [ByteString] -> LBS.ByteString
buildLargeByteString chunks = B.toLazyByteString $
  foldMap B.byteString chunks

-- Avoid intermediate allocations
processLargeFile :: FilePath -> FilePath -> IO ()
processLargeFile input output = 
  BS.readFile input >>= BS.writeFile output . processData
  where
    processData = BS.map toUpper . BS.filter (/= 32)  -- Remove spaces, uppercase

-- Lazy ByteString for streaming
streamProcess :: FilePath -> IO Int64
streamProcess file = do
  content <- LBS.readFile file
  return $ LBS.length $ LBS.filter (/= 10) content  -- Count non-newlines
```

### Text Performance
```haskell
import qualified Data.Text as T
import qualified Data.Text.Lazy as TL
import qualified Data.Text.Lazy.Builder as TB
import qualified Data.Text.IO as T

-- Efficient text building
buildText :: [Text] -> Text  
buildText pieces = TL.toStrict $ TB.toLazyText $
  foldMap TB.fromText pieces

-- Streaming text processing
processTextFile :: FilePath -> IO Text
processTextFile file = do
  content <- T.readFile file  
  return $ T.unlines $ 
           filter (not . T.null) $ 
           map T.strip $ 
           T.lines content

-- Text vs String performance
-- String: Linked list of Char - O(n) for length, indexing
-- Text: UTF-16 encoded array - O(1) for length, fast operations
```

## Fusion and Stream Processing

### List Fusion
```haskell
-- GHC automatically fuses these operations into single pass
efficientPipeline :: [Int] -> [Int]
efficientPipeline = take 100 . filter even . map (*2) . filter (>= 0)

-- Build/foldr fusion
-- map f . map g === map (f . g)  -- Fused automatically
-- filter p . filter q === filter (\x -> p x && q x)

-- Prevent fusion when needed
{-# NOINLINE expensiveFunction #-}
expensiveFunction :: Int -> Int
expensiveFunction x = -- complex computation
```

### Conduit for Streaming
```haskell
import Data.Conduit
import qualified Data.Conduit.List as CL

-- Constant memory usage regardless of input size
processLargeDataset :: FilePath -> FilePath -> IO ()
processLargeDataset input output = runConduitRes $
  sourceFile input
  .| CB.lines  
  .| CL.map processLine
  .| CL.filter isValid
  .| CB.unlines
  .| sinkFile output

-- Memory-bounded operations
slidingWindow :: Int -> Conduit a IO [a]
slidingWindow size = do
  window <- lift $ newIORef []
  awaitForever $ \x -> do
    current <- lift $ readIORef window
    let newWindow = take size (x : current)  
    lift $ writeIORef window newWindow
    yield newWindow
```

## Concurrent Performance

### STM for Shared State
```haskell
import Control.Concurrent.STM

-- Lock-free shared counter
data SharedCounter = SharedCounter (TVar Int)

newSharedCounter :: IO SharedCounter  
newSharedCounter = SharedCounter <$> newTVarIO 0

incrementCounter :: SharedCounter -> STM ()
incrementCounter (SharedCounter var) = modifyTVar' var (+1)

-- Composable transactions
transfer :: TVar Int -> TVar Int -> Int -> STM ()
transfer from to amount = do
  fromBalance <- readTVar from
  when (fromBalance < amount) retry  -- Block until sufficient funds
  modifyTVar from (subtract amount)
  modifyTVar to (+ amount)
```

### Parallel Strategies
```haskell
import Control.Parallel.Strategies
import Control.Parallel

-- Parallel map with controlled evaluation
parMapChunk :: NFData b => Int -> (a -> b) -> [a] -> [b]  
parMapChunk chunkSize f xs = 
  concat $ map (map f) chunks `using` parList rdeepseq
  where
    chunks = chunksOf chunkSize xs

-- Speculative parallelism
fibPar :: Int -> Int  
fibPar n
  | n < 2 = n
  | otherwise = par a (pseq b (a + b))
  where
    a = fibPar (n-1)  -- Computed in parallel
    b = fibPar (n-2)  -- Computed sequentially

-- Divide and conquer parallelism  
mergeSort :: Ord a => [a] -> [a]
mergeSort xs
  | length xs <= 1 = xs
  | otherwise = merge left' right' `using` rpar left' `seq` rpar right'
  where
    (leftHalf, rightHalf) = splitAt (length xs `div` 2) xs
    left' = mergeSort leftHalf  
    right' = mergeSort rightHalf
```

### Async for Concurrency
```haskell
import Control.Concurrent.Async

-- Concurrent HTTP requests
fetchUrls :: [URL] -> IO [Response]
fetchUrls urls = mapConcurrently fetch urls

-- Timeout and cancellation
fetchWithTimeout :: Int -> URL -> IO (Maybe Response)
fetchWithTimeout seconds url = do
  result <- race (threadDelay (seconds * 1000000)) (fetch url)
  case result of
    Left _ -> return Nothing   -- Timeout
    Right response -> return (Just response)

-- Resource pooling  
withResourcePool :: Int -> (Resource -> IO a) -> [Input] -> IO [a]
withResourcePool poolSize action inputs = do  
  semaphore <- newQSem poolSize
  mapConcurrently (\input -> 
    bracket_ (waitQSem semaphore) (signalQSem semaphore) 
             (action input)) inputs
```

## Benchmarking with Criterion

### Basic Benchmarking
```haskell
import Criterion.Main

main :: IO ()
main = defaultMain
  [ bgroup "sorting"
    [ bench "sort 1000 ints" $ whnf sort [1000,999..1]
    , bench "sort 10000 ints" $ whnf sort [10000,9999..1]  
    ]
  , bgroup "data structures"
    [ bench "list sum" $ whnf sum [1..10000]
    , bench "vector sum" $ whnf V.sum (V.fromList [1..10000])
    ]
  ]

-- Different evaluation strategies
benchmarks :: [Benchmark]  
benchmarks =
  [ bench "whnf" $ whnf expensiveFunction input     -- Weak head normal form
  , bench "nf" $ nf expensiveFunction input         -- Full evaluation
  , bench "io" $ whnfIO (expensiveIO input)         -- IO actions
  ]
```

### Advanced Benchmarking
```haskell
-- Environment setup for consistent benchmarking
main :: IO ()  
main = defaultMain
  [ env (setupLargeDataset 100000) $ \ ~dataset ->
      bgroup "processing"
        [ bench "map" $ whnf (map expensiveFunction) dataset
        , bench "vector map" $ whnf (V.map expensiveFunction) (V.fromList dataset)
        ]
  ]

-- Benchmark groups with shared setup
setupLargeDataset :: Int -> IO [Int]
setupLargeDataset size = evaluate (force [1..size])

-- Memory usage benchmarking (with weigh package)
import Weigh

memoryBenchmarks :: IO ()
memoryBenchmarks = mainWith $ do
  func "list sum" sum [1..1000]
  func "vector sum" V.sum (V.fromList [1..1000])
```

## GHC Optimization Flags

### Recommended Optimization Flags
```cabal
-- In cabal file
ghc-options: 
  -O2                    -- Full optimization
  -Wall                  -- All warnings
  -Wcompat               -- Compatibility warnings  
  -Wincomplete-record-updates
  -Wincomplete-uni-patterns
  -Wmissing-home-modules
  -Wpartial-fields
  -Wredundant-constraints

-- For executables
if flag(release)
  ghc-options: 
    -threaded           -- Enable SMP support
    -rtsopts            -- Runtime system options
    -with-rtsopts=-N    -- Use all cores
    -O2 
    -funbox-strict-fields
    -fllvm              -- LLVM backend (if available)
```

### Runtime System Options
```bash
# Garbage collection tuning
./myapp +RTS -A32M      # Increase allocation area (default 1M)
./myapp +RTS -H128M     # Suggest heap size  
./myapp +RTS -G1        # Use single generation GC

# Parallel execution
./myapp +RTS -N4        # Use 4 cores
./myapp +RTS -N         # Use all available cores

# Profiling  
./myapp +RTS -p         # Time profiling
./myapp +RTS -h         # Heap profiling
./myapp +RTS -s         # GC statistics
```

## Common Performance Antipatterns

### Avoid These Patterns
```haskell
-- 1. String concatenation with (++)
badConcat :: [String] -> String  
badConcat = foldr (++) ""  -- O(n²) complexity

-- Fix: Use Text or Builder
goodConcat :: [Text] -> Text
goodConcat = T.concat

-- 2. Repeated list indexing  
badIndexing :: [a] -> [a]
badIndexing xs = [xs !! i | i <- [0..length xs - 1]]

-- Fix: Use vector for indexing or avoid indexing
goodIndexing :: [a] -> [a]  
goodIndexing = id  -- Identity - or use Vector for real indexing needs

-- 3. Excessive laziness in strict contexts
badSum :: [Int] -> Int
badSum [] = 0
badSum (x:xs) = x + badSum xs  -- Stack overflow for large lists

-- Fix: Use accumulator with strictness
goodSum :: [Int] -> Int  
goodSum = go 0
  where
    go !acc [] = acc
    go !acc (x:xs) = go (acc + x) xs

-- 4. Monadic sequence without strictness
badSequence :: [IO Int] -> IO [Int]  
badSequence = sequence  -- Can build up large thunk chains

-- Fix: Force evaluation  
goodSequence :: [IO Int] -> IO [Int]
goodSequence [] = return []
goodSequence (action:actions) = do
  !result <- action
  rest <- goodSequence actions  
  return (result:rest)
```

Performance in Haskell requires understanding the evaluation model and choosing appropriate strictness, data structures, and concurrency primitives for your use case.