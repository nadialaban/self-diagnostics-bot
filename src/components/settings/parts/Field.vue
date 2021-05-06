<template>
  <div :class="col ? 'col-' + col : ''">
    <h5>{{ title }}</h5>
    <slot></slot>
    <div class="invalid-feedback">{{ error }}</div>
  </div>
</template>

<script>
export default {
  name: "Field",
  props: ['col', 'title', 'error']
}
</script>

<style scoped>
div {
  margin-top: 10px;
}
</style>