<template>
  <transition name="fade" mode="out-in">

    <page-header title="Вопрос" :img="current_question.icon">{{ current_question.description }}</page-header>

    <div class="container" v-for="(answer, index) in current_question.answers">
      <button class="btn btn-info btn-block"
              @click="change_state(answer)">{{ answer.answer }}
      </button>
    </div>
  </transition>

  <go-back-buttons :history="history"></go-back-buttons>

  <answer-history :data="history"></answer-history>

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
        'question_id': this.current_question.id
      })

      switch (parts[0]) {
        case 'q':
          this.current_question = this.current_algorithm.questions.find(q => q.id == next_id)
          break;
        case 'r':
          let data = {
            'history': this.history,
            'algorithm_id': this.current_algorithm.id,
            'result_id': next_id
          }
          Event.fire('show-result', data)
          break;
        case 'a':
          this.current_algorithm = this.get_algorithm(next_id)
          this.current_question = this.current_algorithm.questions.find(q => q.id == 1)
          break;
      }
    }
  },
  data() {
    return {
      current_algorithm: null,
      current_question: null,
      history: []
    }
  },
  created() {
    this.current_algorithm = this.get_algorithm(this.data.algorithm_id)
    this.current_question = this.current_algorithm.questions.find(q => q.id == this.data.question_id)
    this.history = this.data.history
  }
}
</script>

<style scoped>
.container {
  margin-top: 5px;
}

.btn {
  margin-top: 15px;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity .2s;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
}

.list-enter-active, .list-leave-active {
  transition: all 1s;
}

.list-enter, .list-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>