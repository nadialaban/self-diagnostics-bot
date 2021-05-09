<template>
  <div>
      <div v-if="state == 'q'">
        <page-header title="Вопрос" :img="current_question.icon">{{ current_question.description }}</page-header>

        <div v-for="(answer, index) in current_question.answers">
          <button class="btn btn-info btn-block"
                  @click="change_state(answer)">{{ answer.answer }}
          </button>
        </div>
      </div>

      <div v-else>
        <div class="text-center" style="margin-bottom: 20px;">
          <img :src="this.img_url(result.color, result.icon)" width="60px">
        </div>

        <div class="alert" :class="get_alert_type()">
          <h4 class="alert-heading text-center">{{ result.title }}</h4>
          <p class="text-justify"> {{ result.description }}</p>
        </div>
      </div>

    <go-back-buttons :history="history" location="test"></go-back-buttons>

    <div v-if="state == 'r'">
      <button class="btn-info btn btn-block"
              @click="send_result()" :disabled="submitted">Завершить
      </button>
      <label class="text-center">После нажатия на кнопку "Завершить" данные
        сохранятся в канале консультирования и отправятся врачу.</label>
    </div>

    <answer-history :data="history"></answer-history>
  </div>
</template>

<script>
import PageHeader from "../common/PageHeader";
import AnswerHistory from "./parts/AnswerHistory";
import GoBackButtons from "./parts/GoBackButtons";

export default {
  name: "Test",
  props: ['data'],
  components: {GoBackButtons, AnswerHistory, PageHeader},
  methods: {
    change_state: function (answer) {
      console.log('ans', answer)
      let parts = answer.next_state.split('-')
      let next_id = parseInt(parts[1])

      this.history.push({
        'description': this.current_question.description,
        'answer': answer.answer,
        'algorithm_id': this.current_algorithm.id,
        'question_id': this.current_question.id,
        'state_id': this.current_algorithm.id + '-' + this.current_question.id
      })
      let data = {}
      switch (parts[0]) {
        case 'q':
          this.current_question = this.current_algorithm.questions.find(q => q.id == next_id)
          break;
        case 'r':
          this.result = this.current_algorithm.results.find(r => r.id == next_id)
          this.state = 'r'
          break;
        case 'a':
          this.change_algorithm(next_id, 1)
          break;
      }
    },
    change_algorithm: function (algorithm_id, question_id) {
      this.axios.get(this.url('/api/algorithm/' + algorithm_id))
          .then(response => this.current_algorithm = response.data)
          .catch(this.process_load_error)
          .finally(() => {
            this.current_question = this.current_algorithm.questions.find(q => q.id == question_id)
          })

    },
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
  data() {
    return {
      current_question: null,
      current_algorithm: null,
      history: [],
      result: null,
      submitted: false,
      state: 'q'
    }
  },
  created() {
    this.history = this.data.history
    this.current_algorithm = this.data.algorithm
    this.current_question = this.current_algorithm.questions.find(q => q.id == this.data.question_id)

    Event.listen('previous-question', (data) => {
      let previous_answer = data.history.pop()
      this.state = 'q'
      console.log('data', data)
      if (previous_answer.algorithm_id == this.current_algorithm.id) {
        this.current_question = this.current_algorithm.questions.find(q => q.id == previous_answer.question_id)
      } else {
        this.change_algorithm(previous_answer.algorithm_id, previous_answer.question_id)
      }
    });
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
}
</style>