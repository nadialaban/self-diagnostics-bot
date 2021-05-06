<template>
  <transition name="fade" mode="out-in">
    <div class="text-center">
      <img :src="this.img_url(result.color, result.icon)" width="60px">
    </div>

    <div class="alert" :class="get_alert_type()">
      <h4 class="alert-heading text-center">{{ result.title }}</h4>
      <p class="text-justify"> {{ result.description }}</p>
    </div>
  </transition>

  <go-back-buttons :history="history"></go-back-buttons>

  <transition name="fade" mode="out-in">
    <button class="btn-info btn btn-block"
            @click="send_result()" :disabled="submitted">Завершить</button>
    <label class="text-center">После нажатия на кнопку "Завершить" данные
      сохранятся в канале консультирования и отправятся врачу.</label>
  </transition>
  <error-block :errors="this.errors"></error-block>
  <answer-history :data="data.history"></answer-history>
</template>

<script>
import GoBackButtons from "./parts/GoBackButtons";
import AnswerHistory from "./parts/AnswerHistory";
import ErrorBlock from "../common/ErrorBlock";

export default {
  name: "Result",
  props: ['data', 'algorithm_title'],
  components: {ErrorBlock, AnswerHistory, GoBackButtons, PageHeader},
  methods: {
    get_alert_type: function () {
      switch (this.result.color) {
        case 'grey':
          return 'alert-secondary';
        case 'green':
          return 'alert-success';
        case 'yellow':
          return 'alert-warning';
        case 'red':
          return 'alert-danger';
      }
    },
    send_result: function () {
      this.submitted = true
      let data = {
        'result': this.result,
        'algorithm_title': this.current_algorithm.title,
        'history': this.history
      }
      this.axios.post(this.url('/api/result'), data)
          .then(r => Event.fire('algorithm-done')).catch(() => {
            this.errors = ['Произошла ошибка сохранения']
            this.submitted = false
          });
    }
  },
  data: function () {
    return {
      current_algorithm: null,
      history: [],
      errors: [],
      submitted: false,
      result: null
    }
  },
  created() {
    this.current_algorithm = this.get_algorithm(this.data.algorithm_id)
    this.history = this.data.history
    this.result = this.current_algorithm.results.find(r => r.id == this.data.result_id)
  }
}
</script>

<style scoped>

label {
  color: red;
  margin-top: 10px;
}

.alert {
  margin-top: 15px;
}

.text-justify {
  white-space: pre-wrap;
}
</style>