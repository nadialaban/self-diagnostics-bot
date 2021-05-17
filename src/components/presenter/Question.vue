<template>
  <div>
    <page-header title="Вопрос" :img="current_question.icon">{{ current_question.description }}</page-header>

    <div v-for="(answer, index) in current_question.answers">
      <button class="btn btn-info btn-block"
              @click="change_state(answer)">{{ answer.answer }}
      </button>
    </div>
    <go-back-buttons :history="history" loc="test" :algorithm="current_algorithm"></go-back-buttons>

    <answer-history v-show="history.length" :data="history"></answer-history>
  </div>
</template>

<script>
import PageHeader from "../common/PageHeader";
import AnswerHistory from "./parts/AnswerHistory";
import GoBackButtons from "./parts/GoBackButtons";

export default {
  name: "Question",
  props: ['data'],
  components: {GoBackButtons, AnswerHistory, PageHeader},
  methods: {
    change_state: function (answer) {
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
          console.log('text')
          Event.fire('show-result', {
            algorithm: this.current_algorithm,
            result: this.current_algorithm.results.find(r => r.id == next_id),
            history: this.history
          })
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
  },
  data() {
    return {
      current_question: null,
      current_algorithm: null,
      history: []
    }
  },
  created() {
    this.history = this.data.history
    this.current_algorithm = this.data.algorithm
    this.current_question = this.current_algorithm.questions.find(q => q.id == this.data.question_id)

    Event.listen('previous-question', (data) => {
      console.log(data.handled)
      if (!data.handled) {
        let previous_answer = this.history.pop()
        console.log(this.history.length)
        if (previous_answer.algorithm_id == this.current_algorithm.id) {
          this.current_question = this.current_algorithm.questions.find(q => q.id == previous_answer.question_id)
        } else {
          this.change_algorithm(previous_answer.algorithm_id, previous_answer.question_id)
        }
        data.handled = true
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