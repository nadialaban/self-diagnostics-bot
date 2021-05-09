<template>
  <div style="margin-bottom: 20px;">
    <card v-for="(algorithm, index) in algorithms"
          :key="algorithm.id"
          :recommended="recommendations[index]"
          :editable="mode == 'admin' ? editable[index] : false"
          :algorithm="algorithm" :mode="mode">
      <div class="input-group-text" v-if="mode == 'admin'">
        <input type="checkbox" :name="algorithm.id"
               v-model="values[index]" @change="changed(index)">
      </div>
    </card>
  </div>
</template>

<script>
import Card from "./Card";

export default {
  name: "AlgorithmSelector",
  components: {Card},
  props: {
    recommendations: {
      required: true
    },
    algorithms: {
      required: true
    },
    mode: {
      required: true
    },
    editable: {
      required: false
    }
  },
  methods: {
    changed: function (index) {
      let data = {
        value: this.values[index],
        index: index
      }
      Event.fire('settings-changed', data)
      console.log(this.clinic_id)
    }
  },
  data() {
    return {
      values: []
    }
  },
  created() {
    this.values = this.recommendations
  }
}
</script>

<style scoped>

</style>