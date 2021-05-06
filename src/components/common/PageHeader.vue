<template>

  <div class="text-center">
    <img v-if="this.img" :src="this.img_url('grey', img)" width="60px">
    <h4 class="text-center">{{ this.title }}</h4>
    <p class="text-justify"><slot></slot></p>
  </div>

</template>

<script>
export default {
  name: "PageHeader",
  props: ['title', 'img']
}
</script>

<style scoped>
.text-justify {
  white-space: pre-wrap;
  margin-top: 15px;
}
</style>