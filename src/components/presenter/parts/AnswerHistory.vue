<template>
  <h6 class="text-center" style="margin-top: 15px;">История ответов</h6>
  <transition-group name="list" tag="p">
    <div class="container" :key="index"
         v-for="(answer, index) in this.history.slice().reverse()">
      <div class="alert alert-secondary">
        <div class="text-justify history-card"
             v-html="format_answer(answer)"></div>
      </div>
    </div>
  </transition-group>

</template>

<script>
export default {
  name: "AnswerHistory"  props: ['data'],
  components: {PageHeader},
  methods: {
    format_answer(answer) {
      return '<strong>Вопрос:</strong> ' + answer.description +
          '\n<strong>Ответ:</strong> ' + answer.answer
    }
  },
  data: function () {
    return {
      history: []
    }
  },
  created() {
    this.history = this.data
  }

}
</script>

<style scoped>
.history-card {
  white-space: pre-wrap;
  margin-left: 15px;
  margin-right:15px;
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