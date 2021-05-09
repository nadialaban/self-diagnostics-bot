<template>
  <div>
    <page-header title="Самодиагностика">Выберите проблему, которая Вас беспокоит...</page-header>
    <loading v-if="!updated"></loading>
    <algorithm-selector v-else mode="patient"
                        :algorithms="algorithms"
                        :recommendations="recommendations"></algorithm-selector>
  </div>
</template>

<script>
import PageHeader from "../common/PageHeader";
import AlgorithmSelector from "../common/AlgorithmSelector";
import Loading from "../Loading";

export default {
  name: "MainPage",
  props: {
    recommended: {
      required: true
    },
    algorithms: {
      required: true
    }
  },
  components: {Loading, AlgorithmSelector, PageHeader},
  data() {
    return {
      updated: false,
      recommendations: null
    }
  },
  created() {
    this.updated = false
    this.recommendations = this.algorithms.map(alg => {
      return this.recommended.includes(alg.id)
    });
    this.updated = true
  }
}
</script>

<style scoped>

</style>