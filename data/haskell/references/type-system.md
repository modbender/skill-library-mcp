# Advanced Type System

## Algebraic Data Types

### Sum Types (Tagged Unions)
```haskell
data Result a b = Success a | Failure b
  deriving stock (Show, Eq, Functor, Foldable, Traversable)
  deriving anyclass (ToJSON, FromJSON)

-- Pattern matching
processResult :: Result User Error -> IO ()
processResult = \case
  Success user -> putStrLn $ "Welcome " <> userName user
  Failure err -> putStrLn $ "Error: " <> show err
```

### Product Types (Records)
```haskell
data User = User
  { userId :: UserId
  , userName :: UserName  
  , userEmail :: Email
  , userCreatedAt :: UTCTime
  } deriving stock (Show, Eq, Generic)
    deriving anyclass (ToJSON, FromJSON)

-- Record update syntax
updateEmail :: Email -> User -> User
updateEmail newEmail user = user { userEmail = newEmail }

-- Lens-compatible fields (with TemplateHaskell)
makeLenses ''User  -- Generates: userId :: Lens' User UserId
```

### Phantom Types for Type Safety
```haskell
data Validated a = Validated a deriving (Show, Eq)
data Unvalidated a = Unvalidated a deriving (Show, Eq)

type ValidatedEmail = Validated Email
type UnvalidatedEmail = Unvalidated Email

validate :: UnvalidatedEmail -> Either ValidationError ValidatedEmail
validate (Unvalidated email) 
  | isValidEmail email = Right (Validated email)
  | otherwise = Left InvalidEmailFormat

-- Forces validation before use
sendEmail :: ValidatedEmail -> Subject -> Body -> IO ()
```

## Generalized Algebraic Data Types (GADTs)

### Type-Safe Expression Trees
```haskell
{-# LANGUAGE GADTs, DataKinds #-}

data Expr a where
  IntLit :: Int -> Expr Int
  BoolLit :: Bool -> Expr Bool
  Add :: Expr Int -> Expr Int -> Expr Int
  Eq :: Eq a => Expr a -> Expr a -> Expr Bool
  If :: Expr Bool -> Expr a -> Expr a -> Expr a

-- Type-safe evaluation
eval :: Expr a -> a
eval (IntLit n) = n
eval (BoolLit b) = b  
eval (Add x y) = eval x + eval y
eval (Eq x y) = eval x == eval y
eval (If cond true false) = if eval cond then eval true else eval false

-- Usage - types enforced at compile time
example :: Expr Int
example = If (Eq (IntLit 5) (Add (IntLit 2) (IntLit 3))) 
             (IntLit 42)
             (IntLit 0)
```

### State Machine Types
```haskell
data State = Locked | Unlocked deriving (Show, Eq)

data Door :: State -> * where
  LockedDoor :: Door 'Locked
  UnlockedDoor :: Door 'Unlocked

unlock :: Code -> Door 'Locked -> Either InvalidCode (Door 'Unlocked)
lock :: Door 'Unlocked -> Door 'Locked  
open :: Door 'Unlocked -> IO (Door 'Unlocked)
-- Cannot open locked door - compile error!
```

## Type Families

### Associated Type Families
```haskell
class Container c where
  type Element c :: *
  empty :: c
  insert :: Element c -> c -> c
  member :: Element c -> c -> Bool

instance Container [a] where
  type Element [a] = a
  empty = []
  insert = (:)
  member = elem

instance Ord a => Container (Set a) where  
  type Element (Set a) = a
  empty = Set.empty
  insert = Set.insert
  member = Set.member
```

## Type Classes

### Multi-Parameter Type Classes
```haskell
{-# LANGUAGE MultiParamTypeClasses, FunctionalDependencies #-}

class Convertible a b | a -> b where
  convert :: a -> b

instance Convertible String Text where
  convert = Text.pack
  
instance Convertible Text String where  
  convert = Text.unpack

-- Functional dependency: a determines b
-- Only one instance per source type allowed
```

### Higher-Kinded Type Classes
```haskell
class Functor f => Applicative f where
  pure :: a -> f a
  (<*>) :: f (a -> b) -> f a -> f b

class Applicative m => Monad m where
  (>>=) :: m a -> (a -> m b) -> m b

-- Monad transformers
class MonadTrans t where
  lift :: Monad m => m a -> t m a

instance MonadTrans (ReaderT r) where
  lift m = ReaderT (\_ -> m)
```

### Type Class Hierarchies
```haskell
class Semigroup a where
  (<>) :: a -> a -> a

class Semigroup a => Monoid a where
  mempty :: a
  
class Functor f => Foldable f where
  foldMap :: Monoid m => (a -> m) -> f a -> m
  
class (Functor t, Foldable t) => Traversable t where  
  traverse :: Applicative f => (a -> f b) -> t a -> f (t b)
```

## Existential Types

### Hiding Type Information
```haskell
{-# LANGUAGE ExistentialQuantification, RankNTypes #-}

data SomeException = forall e. Exception e => SomeException e

instance Show SomeException where
  show (SomeException e) = show e

-- Type-erased containers
data SomeStorable = forall a. Storable a => SomeStorable a

data Widget = forall w. WidgetClass w => Widget w

render :: Widget -> IO ()
render (Widget w) = renderWidget w  -- Uses type class method
```

### Heterogeneous Lists
```haskell
data HList :: [*] -> * where
  HNil :: HList '[]
  HCons :: a -> HList as -> HList (a ': as)

-- Type-safe heterogeneous operations  
hhead :: HList (a ': as) -> a
hhead (HCons x _) = x

htail :: HList (a ': as) -> HList as
htail (HCons _ xs) = xs
```

