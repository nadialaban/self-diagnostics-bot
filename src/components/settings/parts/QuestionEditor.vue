<template>
  <div>
    <field title="Текст вопроса" :error="errors.description">
        <textarea class="form-control text-justify" placeholder="Введите вопрос"
                  :class="!empty(errors.description) && empty(question.description) ? 'is-invalid' : ''"
                  v-model="question.description"></textarea>
    </field>

    <div class="row">
      <field title="Иконка" col="4" :error="errors.icon">
        <select class="custom-select"
                :class="!empty(errors.icon) && empty(question.icon) ? 'is-invalid' : ''"
                v-model="question.icon">
          <option selected disabled value="">Выберите иконку</option>
          <option v-for="icon in icons.symptoms" :value="icon.file_name"
                  :data-thumbnail="img_url('grey', icon.file_name)">
            {{ icon.description }}
          </option>
        </select>
      </field>

      <div class="text-center col-2" style="margin-top: 25px;">
        <img v-if="question.icon" :src="img_url('grey', question.icon)" width="60px">
      </div>
    </div>

    <div style="margin-top: 15px;">
      <h6>Действия</h6>
      <div v-for="(answer,i) in question.answers">
        <div class="form-row">
          <field col="4" :title="'Вариант ответа ' + (i + 1)"
                 :error="errors.answers[i].answer">
            <input type="text" class="form-control" placeholder="Введите ответ"
                   :class="!empty(errors.answers[i].answer) && empty(answer.answer) ? 'is-invalid' : ''"
                   v-model="answer.answer">
          </field>

          <field col="7" :title="'Если ответ \'' + answer.answer + '\', переход к'"
                 :error="errors.answers[i].next_state">
            <select class="custom-select"
                    :class="!empty(errors.answers[i].next_state) && empty(answer.next_state) ? 'is-invalid' : ''"
                    v-model="answer.next_state">
              <option selected disabled value="">Выберите следующий шаг</option>
              <option v-for="q in questions" v-if="q.id != question.id" :value="'q-' + q.id">
                вопросу {{ q.id }}
              </option>
              <option v-for="r in results" :value="'r-' + r.id">
                исходу {{ r.id }} ({{ r.title }})
              </option>
              <option v-for="a in algorithms" :value="'a-' + a.id" v-if="a.id != algorithm_id">
                сценарию "{{ a.title }}"
              </option>
            </select>
          </field>

          <button class="btn col-1" aria-label="Close"
                  v-if="question.answers.length > 2" @click="delete_answer(i)">
            <span aria-hidden="true">&times;</span>
          </button>

        </div>
      </div>
    </div>

    <button class="btn btn-outline-info" @click="add_answer()">
      Добавить вариант ответа
    </button>
  </div>
</template>

<script>
import Field from "./Field";

export default {
  name: "QuestionEditor",
  components: {Field},
  props: ['data', 'results', 'algorithms', 'questions', 'errors', 'icons', 'algorithm_id'],
  methods: {
    delete_answer: function (index) {
      this.question.answers.splice(index, 1)
      this.question_errors.answers.splice(index, 1)
    },
    add_answer: function () {
      this.question.answers.push({
        answer: '',
        next_state: ''
      })
      this.question_errors.answers.push({
        'answer': '',
        'next_state': ''
      })
    }
  },
  data() {
    return {
      question: {},
      question_errors: []
    }
  },
  created() {
    this.question = this.data
    this.question_errors = this.errors
  }
}
</script>

<style scoped>
.btn {
  margin-top: 15px;
}
</style>