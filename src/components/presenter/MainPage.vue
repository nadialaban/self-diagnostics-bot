<template>
  <page-header title="Самодиагностика">Выберите проблему, которая Вас беспокоит...</page-header>
  <algorithm-selector :mode="this.mode"
                      :enabled="this.recommended_algorithms"></algorithm-selector>
</template>

<script>
import PageHeader from "../common/PageHeader";
import AlgorithmSelector from "../common/AlgorithmSelector";

export default {
  name: "MainPage",
  components: {AlgorithmSelector, PageHeader}
}
</script>

<style scoped>

</style>