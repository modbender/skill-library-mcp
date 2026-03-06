#!/bin/bash
NAME="${1:-MyComponent}"
TYPE="${2:-function}"

cat > "$NAME.jsx" << 'JSX'
export default function COMP_NAME(props) {
  return (
    <div>
      <h1>COMP_NAME</h1>
    </div>
  );
}
JSX

sed -i "s/COMP_NAME/$NAME/g" "$NAME.jsx"
echo "✅ React component generated: $NAME.jsx"
