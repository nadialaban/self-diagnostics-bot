<template>
  <div>
    <page-header title="Самодиагностика">Выберите проблему, которая Вас беспокоит...</page-header>

    <algorithm-selector mode="patient"
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
      recommendations: null
    }
  },
  created() {
    this.recommendations = this.algorithms.map(alg => {
      return this.recommended.includes(alg.id.toString())
    });
  }
}
</script>

<style scoped>

</style>