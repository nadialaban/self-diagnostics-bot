<template>
  <div>
    <div class="text-center" style="margin-bottom: 20px;">
      <img :src="this.img_url(result.color, result.icon)" width="60px">
    </div>

    <div class="alert" :class="get_alert_type()">
      <h4 class="alert-heading text-center">{{ result.title }}</h4>
      <p class="text-justify"> {{ result.description }}</p>
    </div>

    <go-back-buttons :history="history" loc="res" :algorithm="data.algorithm"></go-back-buttons>

    <button class="btn-info btn btn-block"
            @click="send_result()" :disabled="submitted">Завершить
    </button>
    <label class="text-center">После нажатия на кнопку "Завершить" данные
      сохранятся в канале консультирования и отправятся врачу.</label>

    <answer-history :data="history"></answer-history>
  </div>

</template>

<script>
import PageHeader from "../common/PageHeader";
import AnswerHistory from "./parts/AnswerHistory";
import GoBackButtons from "./parts/GoBackButtons";

export default {
  name: "Result",
  props: ['data'],
  components: {GoBackButtons, AnswerHistory, PageHeader},
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
        'algorithm_title': this.data.algorithm.title,
        'history': this.history
      }
      this.axios.post(this.url('/api/result'), data)
          .then(r => Event.fire('algorithm-done')).catch(() => {
        this.errors = ['Произошла ошибка сохранения']
        this.submitted = false
      });
    }
  },
  data() {
    return {
      history: [],
      result: [],
      submitted: false
    }
  },
  created() {
    this.history = this.data.history
    this.result = this.data.result
  }
}
</script>

<style scoped>
.btn {
  margin-top: 10px;
}

label {
  color: red;
  margin-top: 10px;
  text-align: center;
  display: block;
}
</style>