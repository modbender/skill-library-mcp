# OOP Traps

- Late static binding — `self::` binds at define time, `static::` at call time
- Abstract class can't instantiate — but CAN have constructor for children
- Trait method conflicts — must resolve with `insteadof` or `as`
- Interface constants — can't override in implementing class
- Clone is shallow — nested objects still shared, implement `__clone`
- `instanceof` with string — `$obj instanceof $className` works dynamically
- Readonly properties — can only set once, in constructor or declaration
- Constructor promotion — `public function __construct(public $x)` declares property
