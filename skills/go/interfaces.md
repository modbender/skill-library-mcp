# Interface Traps

- `var p *MyType = nil; var i interface{} = p` → `i != nil` TRUE — nil trap
- Interface nil only when BOTH type AND value are nil
- Returning nil pointer as interface = non-nil interface
- Pointer receiver `*T` has method — value `T` doesn't satisfy interface
- Interface method signature drift compiles — implicit satisfaction
- Empty interface accepts nil — `var i interface{}=nil; i==nil` true
- Assertion without ok panics — `s := i.(string)` crashes if not string
- Type switch doesn't work with generics — use reflect for `T`
- Asserting to interface checks method set — not underlying type
- Embedded nil pointer exposes methods that panic — check before calling
- Shadowing embedded method is silent — no override warning
- Embedding pointer to interface almost always wrong
- Interface 10+ methods = nobody implements — break into smaller
- Returning interface hides concrete methods — needs assertion
