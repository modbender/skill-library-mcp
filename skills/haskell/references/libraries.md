# Essential Library Ecosystem

## Foundational Data Structures

### Vector - Efficient Arrays
```haskell
import qualified Data.Vector as V
import qualified Data.Vector.Unboxed as U
import qualified Data.Vector.Storable as S

-- Boxed vectors for complex types
userVector :: V.Vector User
userVector = V.fromList [alice, bob, charlie]

-- Unboxed vectors for primitives (memory efficient)
scores :: U.Vector Int  
scores = U.fromList [85, 92, 78, 96]

-- High-performance operations
averageScore :: U.Vector Int -> Double
averageScore scores = 
  fromIntegral (U.sum scores) / fromIntegral (U.length scores)

-- Parallel processing
parallelSum :: U.Vector Int -> Int
parallelSum vec = runEval $ do
  let (left, right) = U.splitAt (U.length vec `div` 2) vec
  leftSum <- rpar (U.sum left)  
  rightSum <- rseq (U.sum right)
  pure (leftSum + rightSum)
```

### Containers - Pure Data Structures
```haskell
import qualified Data.Map.Strict as Map
import qualified Data.Set as Set
import qualified Data.IntMap.Strict as IntMap
import qualified Data.Sequence as Seq

-- Maps for key-value lookups
userMap :: Map UserId User
userMap = Map.fromList [(UserId 1, alice), (UserId 2, bob)]

lookupUser :: UserId -> Map UserId User -> Maybe User
lookupUser = Map.lookup

-- Sets for membership testing
activeUsers :: Set UserId
activeUsers = Set.fromList [UserId 1, UserId 3, UserId 7]

isActive :: UserId -> Bool
isActive userId = userId `Set.member` activeUsers

-- IntMap for integer keys (more efficient)
scoreMap :: IntMap Int
scoreMap = IntMap.fromList [(1, 100), (2, 85), (3, 92)]

-- Sequence for efficient append/prepend
messageQueue :: Seq Message  
messageQueue = Seq.empty
  |> message1
  |> message2
  |> message3
```

### Unordered-Containers - Hash-Based Structures
```haskell
import qualified Data.HashMap.Strict as HM
import qualified Data.HashSet as HS
import Data.Hashable

-- Faster insertion/lookup for non-ordered operations
userCache :: HashMap Text User
userCache = HM.fromList [("alice", alice), ("bob", bob)]

-- Custom Hashable instances
instance Hashable UserId where
  hashWithSalt salt (UserId n) = hashWithSalt salt n

-- HashSet for fast membership
bannedUsers :: HashSet UserId  
bannedUsers = HS.fromList [UserId 5, UserId 12]
```

## Text Processing

### Text - Efficient Unicode Text
```haskell
import qualified Data.Text as T
import qualified Data.Text.IO as T
import qualified Data.Text.Encoding as T

-- Always prefer Text over String
processText :: Text -> Text
processText = T.toUpper . T.strip . T.filter (/= ' ')

-- File I/O
readConfig :: FilePath -> IO Text
readConfig = T.readFile

-- Encoding/decoding
encodeUtf8 :: Text -> ByteString
encodeUtf8 = T.encodeUtf8

decodeUtf8Safe :: ByteString -> Either UnicodeException Text
decodeUtf8Safe = T.decodeUtf8'
```

### ByteString - Efficient Binary Data
```haskell
import qualified Data.ByteString as BS
import qualified Data.ByteString.Lazy as LBS
import qualified Data.ByteString.Builder as B

-- Strict vs lazy
strictRead :: FilePath -> IO ByteString
strictRead = BS.readFile  -- Entire file in memory

lazyRead :: FilePath -> IO LBS.ByteString  
lazyRead = LBS.readFile   -- Streaming

-- Efficient building
buildResponse :: [ByteString] -> LBS.ByteString
buildResponse chunks = B.toLazyByteString $ 
  foldMap B.byteString chunks
```

## JSON and Serialization

### Aeson - JSON Processing
```haskell
{-# LANGUAGE DeriveGeneric, DeriveAnyClass #-}
import Data.Aeson
import GHC.Generics

data User = User 
  { name :: Text
  , age :: Int  
  , email :: Maybe Text
  } deriving stock (Generic, Show)
    deriving anyclass (ToJSON, FromJSON)

-- Custom instances for control
instance ToJSON User where
  toJSON User{..} = object 
    [ "name" .= name
    , "age" .= age
    , "email" .= email  
    ]

instance FromJSON User where
  parseJSON = withObject "User" $ \o -> User
    <$> o .: "name"
    <*> o .: "age"  
    <*> o .:? "email"

-- Parsing with error handling
parseUser :: ByteString -> Either String User
parseUser = eitherDecodeStrict

-- Optics integration
userEmail :: Lens' User (Maybe Text)  
userEmail = key "email" . _Just . _String
```

### Binary - Efficient Binary Serialization
```haskell
import Data.Binary

instance Binary User where
  put User{..} = do
    put name
    put age
    put email
    
  get = User <$> get <*> get <*> get

-- Smaller, faster than JSON for internal communication
serialize :: User -> ByteString
serialize = encode

deserialize :: ByteString -> User  
deserialize = decode
```

## Web Development

### Warp - HTTP Server
```haskell
import Network.Wai
import Network.Wai.Handler.Warp

-- High-performance HTTP server
app :: Application
app request respond = do
  putStrLn $ "Request: " <> show (pathInfo request)
  respond $ responseLBS status200 [] "Hello World"

main :: IO ()  
main = do
  putStrLn "Starting server on port 8080"
  run 8080 app
  
-- With TLS
-- runTLS (tlsSettings "cert.pem" "key.pem") (setPort 443 defaultSettings) app
```

### Servant - Type-Safe Web APIs
```haskell
{-# LANGUAGE DataKinds, TypeOperators #-}
import Servant

type UserAPI = "users" :> Get '[JSON] [User]
          :<|> "users" :> ReqBody '[JSON] User :> Post '[JSON] User
          :<|> "users" :> Capture "id" Int :> Get '[JSON] User

userServer :: Server UserAPI
userServer = listUsers :<|> createUser :<|> getUser
  where
    listUsers = liftIO getAllUsers
    createUser user = liftIO $ saveUser user  
    getUser userId = liftIO $ findUser userId

-- Automatic client generation
userClient :: ClientM [User] 
         :<|> ClientM User 
         :<|> ClientM User
userClient = client (Proxy @UserAPI)

-- Documentation generation  
userDocs :: API
userDocs = docs (Proxy @UserAPI)
```

## Concurrency

### STM - Software Transactional Memory
```haskell
import Control.Concurrent.STM

data Counter = Counter { value :: TVar Int }

newCounter :: IO Counter
newCounter = Counter <$> newTVarIO 0

increment :: Counter -> STM ()
increment counter = modifyTVar' (value counter) (+1)

-- Composable transactions
transfer :: TVar Int -> TVar Int -> Int -> STM ()
transfer fromAccount toAccount amount = do
  fromBalance <- readTVar fromAccount
  when (fromBalance < amount) retry  -- Block until sufficient funds
  modifyTVar fromAccount (subtract amount)
  modifyTVar toAccount (+ amount)

-- Atomic execution
atomicTransfer :: TVar Int -> TVar Int -> Int -> IO ()
atomicTransfer from to amount = atomically $ transfer from to amount
```

### Async - Concurrent Programming
```haskell
import Control.Concurrent.Async

-- Parallel processing
processParallel :: [FilePath] -> IO [ProcessResult]
processParallel files = do
  asyncs <- mapM (async . processFile) files
  mapM wait asyncs

-- Race conditions
fetchWithTimeout :: Int -> IO a -> IO (Maybe a)
fetchWithTimeout timeoutSecs action = do
  result <- race (threadDelay (timeoutSecs * 1000000)) action
  case result of
    Left _ -> pure Nothing    -- Timeout
    Right value -> pure (Just value)

-- Concurrent resource pooling
withResourcePool :: Int -> (Resource -> IO a) -> [Input] -> IO [a]
withResourcePool poolSize action inputs = do
  sem <- newQSem poolSize  -- Limit concurrent operations
  mapConcurrently (\input -> bracket_ (waitQSem sem) (signalQSem sem) 
                                      (action input)) inputs
```

## Database

### PostgreSQL-Simple - PostgreSQL Interface
```haskell
import Database.PostgreSQL.Simple
import Database.PostgreSQL.Simple.FromRow

instance FromRow User where
  fromRow = User <$> field <*> field <*> field

instance ToRow User where  
  toRow User{..} = [toField name, toField age, toField email]

-- Connection management
connectDB :: IO Connection
connectDB = connect defaultConnectInfo 
  { connectDatabase = "myapp"
  , connectUser = "postgres" 
  }

-- Queries with type safety
getUsers :: Connection -> IO [User]
getUsers conn = query_ conn "SELECT name, age, email FROM users"

getUserById :: Connection -> Int -> IO (Maybe User)  
getUserById conn userId = do
  results <- query conn "SELECT name, age, email FROM users WHERE id = ?" 
                        (Only userId)
  case results of
    [user] -> pure (Just user)
    _ -> pure Nothing

-- Prepared statements
insertUser :: Connection -> User -> IO ()
insertUser conn user = do
  _ <- execute conn "INSERT INTO users (name, age, email) VALUES (?, ?, ?)" user
  pure ()
```

## Testing

### Hspec - Behavior-Driven Testing
```haskell
import Test.Hspec
import Test.Hspec.QuickCheck

spec :: Spec
spec = describe "User module" $ do
  describe "validateEmail" $ do
    it "accepts valid emails" $ do
      validateEmail "test@example.com" `shouldBe` Right (Email "test@example.com")
      
    it "rejects invalid emails" $ do  
      validateEmail "invalid" `shouldBe` Left InvalidEmailFormat
      
    prop "roundtrip property" $ \email ->
      either (const True) (\e -> renderEmail e == email) (validateEmail email)

  describe "User creation" $ do
    context "with valid data" $ do
      it "creates user successfully" $ do
        let user = createUser "Alice" 25 "alice@example.com"  
        userName user `shouldBe` "Alice"
        userAge user `shouldBe` 25

-- Running tests
main :: IO ()
main = hspec spec
```

### QuickCheck - Property-Based Testing
```haskell
import Test.QuickCheck

-- Custom generators
instance Arbitrary User where
  arbitrary = User 
    <$> genName
    <*> choose (0, 120)  
    <*> arbitrary
    where
      genName = elements ["Alice", "Bob", "Charlie"]

instance Arbitrary Email where
  arbitrary = Email <$> genEmail
    where  
      genEmail = do
        local <- listOf1 (choose ('a', 'z'))
        domain <- listOf1 (choose ('a', 'z'))
        pure $ local <> "@" <> domain <> ".com"

-- Properties
prop_serializeDeserialize :: User -> Property
prop_serializeDeserialize user = 
  deserialize (serialize user) === user

prop_emailValidation :: Text -> Property  
prop_emailValidation email = 
  case validateEmail email of
    Right (Email e) -> e === email
    Left _ -> property True  -- Invalid input is fine

-- Conditional properties
prop_positiveAge :: User -> Property
prop_positiveAge user = userAge user >= 0 ==> 
  isValidUser user === True
```

### Tasty - Testing Framework
```haskell
import Test.Tasty
import Test.Tasty.HUnit
import Test.Tasty.QuickCheck

tests :: TestTree
tests = testGroup "All Tests"
  [ unitTests
  , propertyTests  
  ]

unitTests :: TestTree
unitTests = testGroup "Unit Tests"
  [ testCase "User validation" $ do
      let result = validateUser "Alice" 25 "alice@example.com"
      result @?= Right (User "Alice" 25 "alice@example.com")
  ]

propertyTests :: TestTree  
propertyTests = testGroup "Property Tests"
  [ testProperty "Serialize roundtrip" prop_serializeDeserialize
  , testProperty "Email validation" prop_emailValidation
  ]

main :: IO ()
main = defaultMain tests
```

## Streaming and Performance

### Conduit - Streaming Data Processing
```haskell
import Data.Conduit
import qualified Data.Conduit.List as CL
import qualified Data.Conduit.Binary as CB

-- Efficient file processing
processLogFile :: FilePath -> FilePath -> IO ()
processLogFile inputFile outputFile = runConduitRes $
  sourceFile inputFile
  .| CB.lines
  .| CL.map (processLogLine . decodeUtf8)
  .| CL.filter isImportantLog  
  .| CL.map encodeUtf8
  .| CB.unlines
  .| sinkFile outputFile

-- Memory-efficient aggregation
countWords :: FilePath -> IO Int
countWords file = runConduitRes $
  sourceFile file  
  .| CB.lines
  .| CL.concatMap T.words
  .| CL.length
```

This ecosystem provides the foundation for most Haskell applications, with each library designed for composability and type safety.
