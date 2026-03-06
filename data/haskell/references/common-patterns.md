# Common Patterns and Idioms

## Monad Transformers

### The Transformer Stack
```haskell
-- Building application context
type App = ReaderT AppConfig (ExceptT AppError (StateT AppState IO))

runApp :: AppConfig -> AppState -> App a -> IO (Either AppError (a, AppState))
runApp config initState action = 
  runStateT (runExceptT (runReaderT action config)) initState

-- Automatic lifting with mtl constraints
fetchUser :: (MonadReader AppConfig m, MonadError AppError m, MonadIO m) 
          => UserId -> m User
fetchUser userId = do
  dbConn <- asks configDbConnection
  result <- liftIO $ queryUser dbConn userId
  case result of
    Nothing -> throwError (UserNotFound userId)
    Just user -> pure user
```

### Common Transformer Combinations
```haskell
-- Web application stack
type WebM = ReaderT Request (ExceptT HttpError (WriterT [LogMessage] IO))

-- Parser with backtracking
type Parser = StateT ParseState (ExceptT ParseError (Writer [Warning]))

-- STM-based concurrent computation  
type ConcurrentApp = ReaderT Config (ExceptT AppError STM)
```

## MTL Style vs Transformers

### MTL Style (Preferred)
```haskell
-- Abstract over concrete transformers
class Monad m => MonadUser m where
  getUser :: UserId -> m (Maybe User)
  saveUser :: User -> m ()

instance MonadUser App where
  getUser userId = do
    conn <- asks dbConnection
    liftIO $ Database.queryUser conn userId
    
  saveUser user = do
    conn <- asks dbConnection  
    liftIO $ Database.insertUser conn user

-- Easy to test with pure instances
instance MonadUser (State [User]) where
  getUser userId = gets (find (\u -> userId u == userId))
  saveUser user = modify (user :)
```

### Avoiding Transformer Stack Explosion
```haskell
-- Instead of ReaderT Config (StateT State (ExceptT Error IO))
-- Use a single transformer with combined context
data AppContext = AppContext
  { appConfig :: Config
  , appState :: IORef State  -- Mutable state via IORef
  }

type App = ReaderT AppContext (ExceptT Error IO)

getState :: App State
getState = do
  stateRef <- asks appState
  liftIO $ readIORef stateRef

modifyState :: (State -> State) -> App ()  
modifyState f = do
  stateRef <- asks appState
  liftIO $ modifyIORef stateRef f
```

## ReaderT Pattern

### Configuration Management
```haskell
data AppConfig = AppConfig
  { configDatabase :: DatabaseConfig
  , configLogging :: LogConfig
  , configAuth :: AuthConfig
  } deriving stock (Generic)
    deriving anyclass (FromJSON)

-- Environment-specific configs
loadConfig :: Environment -> IO AppConfig
loadConfig env = do
  configFile <- getConfigPath env
  eitherDecodeFileStrict configFile >>= either throwIO pure

-- Dependency injection via Reader
class HasDatabase env where
  databaseConfig :: env -> DatabaseConfig

class HasLogging env where  
  loggingConfig :: env -> LogConfig

instance HasDatabase AppConfig where
  databaseConfig = configDatabase

instance HasLogging AppConfig where
  loggingConfig = configLogging

-- Functions depend only on what they need
connectDb :: (MonadReader env m, HasDatabase env, MonadIO m) => m Connection
connectDb = do
  dbConfig <- asks databaseConfig
  liftIO $ connect dbConfig
```

## Effect Systems

### Free Monads for Testability
```haskell
{-# LANGUAGE DeriveFunctor, TemplateHaskell #-}

data UserAction a
  = GetUser UserId (User -> a)
  | SaveUser User a  
  | DeleteUser UserId a
  deriving Functor

type UserProgram = Free UserAction

-- Smart constructors
getUser :: UserId -> UserProgram User
getUser userId = liftF $ GetUser userId id

saveUser :: User -> UserProgram ()
saveUser user = liftF $ SaveUser user ()

-- Program composition
updateUserEmail :: UserId -> Email -> UserProgram ()
updateUserEmail userId newEmail = do
  user <- getUser userId
  let updatedUser = user { userEmail = newEmail }
  saveUser updatedUser

-- Different interpreters for different contexts
interpretIO :: UserProgram a -> ReaderT DatabaseConfig IO a
interpretIO = iterM $ \case
  GetUser userId next -> do
    conn <- ask
    user <- liftIO $ queryUser conn userId
    next user
  SaveUser user next -> do
    conn <- ask  
    liftIO $ insertUser conn user
    next
  DeleteUser userId next -> do
    conn <- ask
    liftIO $ deleteUser conn userId
    next

-- Pure interpreter for testing
interpretPure :: UserProgram a -> State [User] a
interpretPure = iterM $ \case
  GetUser userId next -> do
    users <- get
    let user = find ((== userId) . userId) users
    next user
  SaveUser user next -> do
    modify (user :)
    next
```

### Extensible Effects with Polysemy
```haskell
{-# LANGUAGE TemplateHaskell, GADTs, FlexibleContexts #-}
import Polysemy

data UserEffect m a where
  GetUser :: UserId -> UserEffect m (Maybe User)  
  SaveUser :: User -> UserEffect m ()

makeSem ''UserEffect  -- Generates smart constructors

-- Business logic independent of interpretation
updateUserProgram :: Member UserEffect r => UserId -> Email -> Sem r ()
updateUserProgram userId newEmail = do
  maybeUser <- getUser userId
  case maybeUser of
    Nothing -> pure ()  -- or throw error
    Just user -> saveUser user { userEmail = newEmail }

-- Database interpreter
runUserDb :: Member (Embed IO) r => DatabaseConfig -> Sem (UserEffect : r) a -> Sem r a
runUserDb config = interpret $ \case
  GetUser userId -> embed $ queryUserDb config userId
  SaveUser user -> embed $ saveUserDb config user

-- Pure interpreter  
runUserPure :: Sem (UserEffect : r) a -> Sem r a
runUserPure = interpret $ \case
  GetUser userId -> pure Nothing  -- simplified
  SaveUser _ -> pure ()
```

## Optics and Lenses

### Basic Lens Usage
```haskell
{-# LANGUAGE TemplateHaskell #-}
import Control.Lens

data Address = Address
  { _street :: Text
  , _city :: Text  
  , _country :: Text
  } deriving (Show, Eq)

data Person = Person  
  { _name :: Text
  , _age :: Int
  , _address :: Address
  } deriving (Show, Eq)

makeLenses ''Address
makeLenses ''Person

-- Deep updates without nested record syntax
updateCity :: Text -> Person -> Person  
updateCity newCity = address . city .~ newCity

-- Multiple updates
movePerson :: Text -> Text -> Person -> Person
movePerson newStreet newCity = 
  (address . street .~ newStreet) . (address . city .~ newCity)

-- Traversals over structures
allCities :: [Person] -> [Text]
allCities people = people ^.. traverse . address . city
```

### Prisms for Sum Types
```haskell
data Result a = Success a | Failure Text deriving (Show, Eq)

makePrisms ''Result  -- Generates _Success and _Failure prisms

-- Pattern matching with prisms
processResult :: Result Int -> Text
processResult result = case result of
  r | Just value <- r ^? _Success -> "Got: " <> show value  
  r | Just err <- r ^? _Failure -> "Error: " <> err
  _ -> "Unknown"  -- Won't happen but exhaustiveness checker

-- Traversal over successes only
incrementSuccesses :: [Result Int] -> [Result Int]
incrementSuccesses = map (_Success %~ (+ 1))
```

### Custom Optics
```haskell
-- Iso for bidirectional conversion
userNameIso :: Iso' User Text
userNameIso = iso getUserName (\name -> User name)

-- Lens for computed properties
ageBracket :: Lens' Person Text  
ageBracket = lens getAgeBracket setAgeBracket
  where
    getAgeBracket person
      | person ^. age < 18 = "Minor"
      | person ^. age < 65 = "Adult"  
      | otherwise = "Senior"
    setAgeBracket person bracket = person  -- Read-only in practice
```

## Newtype Patterns

### Domain-Driven Design with Newtypes
```haskell
newtype UserId = UserId Int
  deriving newtype (Show, Eq, Ord, Hashable, ToJSON, FromJSON)
  deriving stock (Generic)

newtype EmailAddress = EmailAddress Text
  deriving newtype (Show, Eq, IsString)
  deriving stock (Generic)

-- Smart constructors for validation
mkEmailAddress :: Text -> Either ValidationError EmailAddress
mkEmailAddress email
  | "@" `Text.isInfixOf` email = Right (EmailAddress email)
  | otherwise = Left InvalidEmail

-- Prevents mixing up parameters
sendEmail :: EmailAddress -> Subject -> Body -> IO ()
-- Can't accidentally pass UserId where EmailAddress expected
```

### Phantom Types for State
```haskell
data ValidationState = Validated | Unvalidated

newtype Form (s :: ValidationState) = Form (Map Text Text)
  deriving newtype (Show, Eq)

type ValidatedForm = Form 'Validated
type UnvalidatedForm = Form 'Unvalidated

validate :: UnvalidatedForm -> Either [ValidationError] ValidatedForm
validate (Form fields) = do
  validateRequired fields
  validateFormats fields  
  pure (Form fields)

-- Only validated forms can be processed  
processForm :: ValidatedForm -> IO ()
processForm (Form fields) = do
  -- Process with confidence that validation occurred
  pure ()
```

## Type-Level Programming Patterns

### Singleton Pattern for Runtime Type Info
```haskell
{-# LANGUAGE GADTs, DataKinds, KindSignatures #-}

data Format = JSON | XML | YAML

data SFormat (f :: Format) where
  SJSON :: SFormat 'JSON
  SXML :: SFormat 'XML
  SYAML :: SFormat 'YAML

class SingI (f :: Format) where
  sing :: SFormat f

instance SingI 'JSON where sing = SJSON
instance SingI 'XML where sing = SXML  
instance SingI 'YAML where sing = SYAML

-- Format-specific encoding
encode :: SingI f => SFormat f -> Value -> ByteString
encode SJSON = Aeson.encode
encode SXML = xmlEncode  
encode SYAML = Yaml.encode

-- Type determines runtime behavior
encodeAs :: forall f. SingI f => Value -> ByteString  
encodeAs = encode (sing @f)
```

### HList for Heterogeneous Collections
```haskell
data HList :: [*] -> * where
  HNil :: HList '[]
  HCons :: a -> HList as -> HList (a ': as)

type family All (c :: * -> Constraint) (xs :: [*]) :: Constraint where
  All c '[] = ()
  All c (x ': xs) = (c x, All c xs)

-- Operations constrained to work on all elements
hmap :: (forall a. c a => a -> b) -> HList xs -> [b]
hmap _ HNil = []
hmap f (HCons x xs) = f x : hmap f xs

showAll :: All Show xs => HList xs -> [String]
showAll = hmap show

example :: HList '[Int, Bool, Text]
example = HCons 42 (HCons True (HCons "hello" HNil))

-- Type-safe element access
class HIndex (n :: Nat) (xs :: [*]) where
  type Index n xs :: *
  hindex :: HList xs -> Index n xs
```

## Error Handling Patterns

### Validation Applicative
```haskell
data ValidationError = EmailInvalid | NameTooShort | AgeTooLow
  deriving (Show, Eq)

-- Accumulate all errors, not just first
data Validation e a = Failure [e] | Success a
  deriving (Show, Eq, Functor)

instance Semigroup e => Applicative (Validation e) where
  pure = Success
  Success f <*> Success a = Success (f a)
  Success _ <*> Failure es = Failure es
  Failure es <*> Success _ = Failure es  
  Failure es1 <*> Failure es2 = Failure (es1 <> es2)

-- Validate all fields
validateUser :: Text -> Text -> Int -> Validation ValidationError User
validateUser email name age = User 
  <$> validateEmail email
  <*> validateName name  
  <*> validateAge age
  where
    validateEmail e | "@" `Text.isInfixOf` e = Success e
                   | otherwise = Failure [EmailInvalid]
    
    validateName n | Text.length n >= 2 = Success n
                  | otherwise = Failure [NameTooShort]
    
    validateAge a | a >= 0 = Success a
                 | otherwise = Failure [AgeTooLow]
```

### Exception Hierarchy
```haskell
data AppException 
  = DatabaseException DatabaseError
  | ValidationException ValidationError  
  | NetworkException NetworkError
  deriving stock (Show, Generic)
  deriving anyclass (Exception)

-- Specific handlers for different error types
handleApp :: IO a -> IO (Either AppException a)
handleApp action = do
  result <- try action
  pure $ case result of
    Left (e :: AppException) -> Left e
    Right value -> Right value

-- Selective catching
catchDatabase :: IO a -> (DatabaseError -> IO a) -> IO a
catchDatabase action handler = action `catch` \case
  DatabaseException dbErr -> handler dbErr
  otherErr -> throwIO otherErr
```

## Concurrency Patterns

### STM for Transactional Memory
```haskell
import Control.Concurrent.STM

data Account = Account { balance :: TVar Int }

transfer :: Account -> Account -> Int -> STM ()
transfer from to amount = do
  fromBalance <- readTVar (balance from)
  toBalance <- readTVar (balance to)
  
  when (fromBalance < amount) $ 
    throwSTM InsufficientFunds
    
  writeTVar (balance from) (fromBalance - amount)
  writeTVar (balance to) (toBalance + amount)

-- Atomically execute transaction
safeTransfer :: Account -> Account -> Int -> IO (Either SomeException ())
safeTransfer from to amount = try $ atomically $ transfer from to amount
```

### Async Coordination
```haskell
import Control.Concurrent.Async

-- Parallel processing with error handling
processParallel :: [Input] -> IO [Either Error Result]
processParallel inputs = do
  asyncs <- mapM (async . processOne) inputs
  mapM waitCatch asyncs
  where
    processOne input = do
      result <- process input
      evaluate result  -- Force evaluation

-- Race multiple operations
firstSuccess :: [IO a] -> IO (Maybe a)
firstSuccess actions = do
  asyncs <- mapM async actions
  result <- waitAnySuccess asyncs
  mapM_ cancel asyncs
  pure result
```

These patterns represent the core idioms of idiomatic Haskell development, emphasizing type safety, composability, and explicit error handling.