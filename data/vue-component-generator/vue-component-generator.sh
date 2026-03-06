#!/bin/bash
NAME="${1:-MyComponent}"

cat > "$NAME.vue" << 'VUE'
<template>
  <div class="COMP_NAME">
    <h1>COMP_NAME</h1>
  </div>
</template>

<script setup>
</script>

<style scoped>
.COMP_NAME {
}
</style>
VUE

sed -i "s/COMP_NAME/$NAME/g" "$NAME.vue"
echo "✅ Vue component generated: $NAME.vue"
