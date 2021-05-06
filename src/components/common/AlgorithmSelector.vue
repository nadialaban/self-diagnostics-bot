<template>
  <card v-for="(algorithm, index) in this.cur_algorithms"
        :recommended="this.recommendations[index]"
        :editable="this.editable[index]"
        :algorithm="algorithm" :mode="this.mode">
    <div class="input-group-text">
      <input type="checkbox" :name="this.algorithm.id"
             :value="this.recommendations[index]" @change="changed()">
    </div>
  </card>
</template>

<script>
import Card from "./Card";

export default {
  name: "AlgorithmSelector",
  components: {Card},
  props: ['enabled', 'mode'],
  methods: {
    changed: function () {
      Event.fire('settings-changed')
    }
  },
  data() {
    return {
      cur_algorithms: [],
      recommendations: [],
      editable: []
    }
  },
  created() {
    this.cur_algorithms = this.mode == 'patient' ?
        this.get_enabled_algorithms() : this.get_algorithms()

    this.cur_algorithms.sort(function (x, y) {
      return this.enabled.includes(x.id) === this.enabled.includes(y.id) ?
          0 : this.enabled.includes(x.id) ? -1 : 1;
    });

    this.recommendations = this.cur_algorithms.map(alg => this.enabled.includes(alg.id))
    this.editable = this.cur_algorithms.map(alg => this.clinic_id == alg.clinic_id)
  }
}
</script>

<style scoped>

</style>