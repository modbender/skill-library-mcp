# GHC Extensions Reference

## Essential Extensions (Always Enable)

### OverloadedStrings
```haskell
{-# LANGUAGE OverloadedStrings #-}
import qualified Data.Text as T

-- String literals become polymorphic
text :: Text
text = "hello"  -- Automatically Text.pack "hello"

bytestring :: ByteString  
bytestring = "hello"  -- Automatically ByteString.pack "hello"

-- Works with any IsString instance
class IsString a where
  fromString :: String -> a
```

### DerivingStrategies
```haskell
{-# LANGUAGE DerivingStrategies #-}
{-# LANGUAGE GeneralizedNewtypeDeriving #-}

newtype UserId = UserId Int
  deriving stock (Show, Eq, Ord)      -- Use built-in deriving
  deriving newtype (Hashable, ToJSON) -- Unwrap newtype
  deriving anyclass (FromJSON)        -- Use default implementation

-- Always be explicit about deriving strategy
data User = User Text Int
  deriving stock (Show, Eq, Generic)
  deriving anyclass (ToJSON, FromJSON)
```

### LambdaCase
```haskell
{-# LANGUAGE LambdaCase #-}

-- Concise pattern matching in lambda
parseResult :: Text -> Either Error Value
parseResult input = case parse input of
  \case  -- No need to name the parameter
    Left err -> Left (ParseError err)
    Right val -> Right val

-- Useful with higher-order functions
processResults :: [Either Error Value] -> [Value]
processResults = mapMaybe $ \case
  Left _ -> Nothing
  Right val -> Just val
```

### MultiWayIf  
```haskell
{-# LANGUAGE MultiWayIf #-}

gradeToLetter :: Int -> Char
gradeToLetter grade = if
  | grade >= 90 -> 'A'
  | grade >= 80 -> 'B'  
  | grade >= 70 -> 'C'
  | grade >= 60 -> 'D'
  | otherwise -> 'F'
```

## Type System Extensions

### RankNTypes (Higher-Rank Polymorphism)
```haskell
{-# LANGUAGE RankNTypes #-}

-- Functions that take polymorphic functions as arguments
applyToEach :: (forall a. Show a => a -> String) -> (Int, Bool) -> (String, String)
applyToEach f (x, y) = (f x, f y)

-- Continuation-passing style
withResource :: (forall a. Resource -> IO a) -> IO a
withResource action = bracket acquireResource releaseResource action

-- Church encoding  
type ChurchInt = forall a. (a -> a) -> a -> a

churchZero :: ChurchInt
churchZero = \f x -> x

churchOne :: ChurchInt  
churchOne = \f x -> f x
```

### ExistentialQuantification
```haskell
{-# LANGUAGE ExistentialQuantification #-}

-- Hide specific type information
data SomeException = forall e. Exception e => SomeException e

-- Type-erased collections
data Widget = forall w. Renderable w => Widget w

renderWidget :: Widget -> IO ()
renderWidget (Widget w) = render w

-- Existential with constraints
data SomeStorable = forall a. Storable a => SomeStorable a

sizeOfSomeStorable :: SomeStorable -> Int  
sizeOfSomeStorable (SomeStorable x) = sizeOf x
```

## Constraint Extensions

### FlexibleContexts & FlexibleInstances
```haskell
{-# LANGUAGE FlexibleContexts #-}
{-# LANGUAGE FlexibleInstances #-}

-- Allow complex constraints
complexFunction :: (MonadReader Config m, MonadError AppError m, MonadIO m) 
                => UserId -> m User
complexFunction userId = do
  config <- ask
  -- ... implementation

-- Allow overlapping instances (be careful!)  
instance Show (a -> b) where
  show _ = "<function>"

instance {-# OVERLAPPING #-} Show (Int -> Int) where
  show _ = "<int function>"
```

## Pattern Extensions

### PatternSynonyms
```haskell
{-# LANGUAGE PatternSynonyms #-}

-- Bidirectional pattern synonyms
pattern Empty :: [a]
pattern Empty = []

pattern NonEmpty :: a -> [a] -> [a]  
pattern NonEmpty x xs = x:xs

{-# COMPLETE Empty, NonEmpty #-}  -- Tell GHC patterns are exhaustive

safeLast :: [a] -> Maybe a
safeLast Empty = Nothing
safeLast (NonEmpty x Empty) = Just x  
safeLast (NonEmpty _ xs) = safeLast xs

-- Unidirectional patterns for complex matching
pattern AuthenticatedUser :: Text -> Request -> User
pattern AuthenticatedUser username request <- 
  (lookupUser request -> Just (User username _ _))
```

## Deriving Extensions

### DeriveGeneric
```haskell
{-# LANGUAGE DeriveGeneric #-}
import GHC.Generics

data User = User 
  { name :: Text
  , age :: Int
  } deriving (Generic)

-- Automatic JSON instances
instance ToJSON User
instance FromJSON User

-- Generic programming
genericShow :: (Generic a, GShow (Rep a)) => a -> String
genericShow = gshow . from
```

### DeriveFunctor, DeriveFoldable, DeriveTraversable
```haskell
{-# LANGUAGE DeriveFunctor, DeriveFoldable, DeriveTraversable #-}

data Tree a = Leaf a | Branch (Tree a) (Tree a)
  deriving (Functor, Foldable, Traversable)

-- Automatic instances generated
mapTree :: (a -> b) -> Tree a -> Tree b
mapTree = fmap  -- Uses derived Functor

sumTree :: Num a => Tree a -> a  
sumTree = sum   -- Uses derived Foldable
```

### DeriveAnyClass
```haskell
{-# LANGUAGE DeriveAnyClass #-}

class Serializable a where
  serialize :: a -> ByteString
  deserialize :: ByteString -> Either String a
  
-- Use default implementations
data Point = Point Int Int
  deriving (Generic, Serializable)  -- Uses DeriveAnyClass
```

## Template Haskell Extensions

### TemplateHaskell
```haskell
{-# LANGUAGE TemplateHaskell #-}
import Control.Lens

data User = User
  { _userName :: Text
  , _userAge :: Int
  , _userEmail :: Text  
  } deriving (Show, Eq)

makeLenses ''User  -- Generates lenses at compile time

-- Usage  
updateUserAge :: Int -> User -> User
updateUserAge newAge = userAge .~ newAge
```

## Syntax Extensions

### RecordWildCards
```haskell
{-# LANGUAGE RecordWildCards #-}

data User = User 
  { userName :: Text
  , userAge :: Int
  , userEmail :: Text
  }

-- Automatic pattern matching and binding
processUser :: User -> Text
processUser User{..} = userName <> " (" <> show userAge <> ")"

-- In construction  
createUser :: Text -> Int -> Text -> User
createUser userName userAge userEmail = User{..}
```

### BangPatterns
```haskell
{-# LANGUAGE BangPatterns #-}

-- Force evaluation in pattern matching
strictMap :: (a -> b) -> [a] -> [b]
strictMap _ [] = []
strictMap f (!x:xs) = f x : strictMap f xs

-- Strict let bindings
processData :: [Int] -> Int  
processData xs = 
  let !len = length xs    -- Evaluated immediately
      !sum' = sum xs
  in sum' `div` len
```

## Extension Warnings

### Safe vs Unsafe Extensions
```haskell
-- Generally safe extensions
{-# LANGUAGE OverloadedStrings #-}    -- Always safe
{-# LANGUAGE LambdaCase #-}           -- Pure syntax
{-# LANGUAGE DerivingStrategies #-}   -- Explicit is better

-- Use with caution
{-# LANGUAGE UndecidableInstances #-}  -- Can cause infinite loops
{-# LANGUAGE IncoherentInstances #-}   -- Breaks type system guarantees  
{-# LANGUAGE OverlappingInstances #-}  -- Use OVERLAPPING pragma instead
```

These extensions unlock Haskell's advanced type system features while maintaining the language's strong guarantees about correctness and performance.
