<template>
  <page-header img="edit"
               :title="(this.action.startsWith('create') ? 'Создание' : 'Редактирование') + ' алгоритма'"></page-header>

  <!-- Общая информация -->

  <div class="row">
    <field title="Название" col="6" :error="errors.title">
      <input type="text" class="form-control"
             :class="!this.empty(errors.title) && (this.empty(algorithm.title) || algorithm_exists()) ? 'is-invalid' : ''"
             placeholder="Введите название сценария самодиагностики"
             v-model="algorithm.title">
    </field>

    <field title="Иконка" col="4" :error="errors.icon">
      <select class="custom-select"
              :class="!this.empty(errors.icon) && this.empty(algorithm.icon) ? 'is-invalid' : ''"
              v-model="algorithm.icon">
        <option selected disabled value="">Выберите иконку</option>
        <option v-for="icon in icons.symptoms" :value="icon.file_name"
                :data-thumbnail="this.img_url('grey', icon.file_name)">
          {{ icon.description }}
        </option>
      </select>
    </field>

    <div class="text-center col-2" style="margin-top: 25px;">
      <img v-show="algorithm.icon" :src="this.img_url('grey', algorithm.icon)" width="60px">
    </div>

  </div>

  <field title="Описание для пациента" :error="errors.patient_description">
    <textarea class="form-control text-justify" rows="5"
              :class="!this.empty(errors.patient_description) && this.empty(algorithm.patient_description) ? 'is-invalid' : ''"
              placeholder="Введите описание сценария самодиагностики для пациента"
              v-model="algorithm.patient_description"></textarea>
  </field>

  <field title="Описание для врача" :error="errors.doctor_description">
    <textarea class="form-control text-justify" rows="5"
              :class="!this.empty(errors.doctor_description) && this.empty(algorithm.doctor_description) ? 'is-invalid' : ''"
              placeholder="Введите описание сценария самодиагностики для врача"
              v-model="algorithm.doctor_description"></textarea>
  </field>

  <array-editor title="Вопросы" type="q"
                :data="algorithm.questions"
                :results="algorithm.results" :algorithms="algorithms"
                :errors="errors.questions"></array-editor>
  <array-editor title="Исходы" type="r"
                :data="algorithm.results"
                :errors="errors.results"></array-editor>

  <field title="Ключевые слова и фразы">
    <textarea class="form-control text-justify" rows="5"
              placeholder="Вводите ключевые фразы с новой строчки. Интеллектуальный агент будет искать их в сообщении пациента, чтобы предложить пройти этот сценарий."
              v-model="algorithm.keywords"></textarea>
  </field>

  <!-- Кнопка сохранения -->
  <button class="btn btn-block btn-info"
          :disabled="submitted"
          @click="save_algorithm()">Сохранить
  </button>

  <!-- Кнопка удаления -->
  <button class="btn btn-block btn-secondary"
          v-if="!algorithm.depends"
          :disabled="submitted"
          @click="delete_algorithm()">Удалить
  </button>

  <!-- Кнопка возвращения -->
  <button class="btn btn-block btn-outline-info"
          :disabled="submitted"
          @click="go_back()">Вернуться
  </button>

</template>

<script>
import PageHeader from "../common/PageHeader";
import Field from "./parts/Field";
import ArrayEditor from "./parts/ArrayEditor";

export default {
  name: "Editor",
  components: {ArrayEditor, Field, PageHeader},
  props: ['data', 'action'],
  methods: {
    algorithm_exists: function () {
      return this.algorithms.find(alg => alg.title == this.algorithm.title)
    },
    get_question_errors: function () {
      return {
        description: '',
        answers: [{
          answer: '',
          next_state: ''
        }, {
          answer: '',
          next_state: ''
        }],
        icon: ''
      }
    },
    get_result_errors: function () {
      return {
        title: '',
        description: '',
        color: '',
        message: '',
        icon: ''
      }
    },
    delete_algorithm: function () {
      this.$confirm({
        message: `Вы уверены? Сценарий удалится для всех пациентов. Действие нельзя отменить!`,
        button: {
          no: 'Нет',
          yes: 'Да'
        },
        callback: confirm => {
          if (confirm) {
            this.axios.post(this.url('/api/settings/delete_algorithm'), this.algorithm)
                .then(r => Event.fire('delete-algorithm'));
          }
        }
      })
    },
    save_algorithm: function () {
      this.submitted = true
      if (this.validate()) {
        for (let i = 0; i < this.algorithm.questions.length; i++) {
          for (let j = 0; j < this.algorithm.questions[i].length; j++) {
            if (this.algorithm.questions[i].answers[j].next_state.startsWith('a')) {
              let alg_id = parseInt(this.algorithm.questions[i].answers[j].next_state.split('-')[1])
              this.algorithm.depended_algorithms.push(alg_id)
            }
          }
        }

        this.axios.post(this.url('/api/settings/save_algorithm'), this.algorithm)
            .then(r => Event.fire('save-algorithm'));
      }
      this.submitted = false
    },
    validate: function () {
      let required = '* Обязательное поле'
      let flag = false

      this.errors.title = this.empty(this.algorithm.title) ?
          required : this.algorithm_exists() ?
              '* Сценарий с таким названием уже существует' : ''
      this.errors.icon = this.empty(this.algorithm.icon) ? required : ''
      this.errors.patient_description = this.empty(this.algorithm.patient_description) ? required : ''
      this.errors.doctor_description = this.empty(this.algorithm.doctor_description) ? required : ''

      for (let i = 0; i < this.algorithm.questions.length; i++) {
        this.errors.questions[i].description = this.empty(this.algorithm.questions[i].title) ? required : ''
        this.errors.questions[i].icon = this.empty(this.algorithm.questions[i].icon) ? required : ''

        if (this.errors.questions[i].description || this.errors.questions[i].icon)
          flag = true

        for (let j = 0; j < this.algorithm.questions[i].answers.length; j++) {
          this.errors.questions[i].answers[j].answer = this.empty(this.algorithm.questions[i].answers[j].answer) ? required : ''
          this.errors.questions[i].answers[j].next_state = this.empty(this.algorithm.questions[i].answers[j].next_state) ? required : ''

          if (this.errors.questions[i].answers[j].answer || this.errors.questions[i].answers[j].next_state)
            flag = true
        }
      }

      return !(flag || this.errors.title || this.errors.icon ||
          this.errors.patient_description || this.errors.doctor_description);
    },
    go_back: function () {
      this.$confirm({
        message: `Вы уверены? Все несохраненные данные будут утеряны!`,
        button: {
          no: 'Нет',
          yes: 'Да'
        },
        callback: confirm => {
          if (confirm) {
            Event.fire('bak-to-settings')
          }
        }
      })
    }
  },
  data() {
    return {
      algorithm: null,
      algorithms: [],
      icons: {},
      errors: {},
      submitted: false
    }
  },
  created() {
    this.algorithm = this.data.algorithm
    this.algorithms = this.get_algorithms()

    this.icons = this.get_icons()

    this.errors = {
      title: '',
      icon: '',
      patient_description: '',
      doctor_description: '',
      questions: new Array(this.algorithm.questions.length),
      results: new Array(this.algorithm.results.length)
    }

    this.errors.questions.fill(this.get_question_errors())
    this.errors.results.fill(this.get_result_errors())

    Event.listen('delete-result', result_id => {
      this.algorithm.questions = this.algorithm.questions.map(obj => {
        obj.answers = obj.answers.map(ans => {
          if (ans.next_state.startsWith('r')) {
            let next_id = parseInt(ans.next_state.split('-')[1])
            if (next_id == result_id)
              ans.next_state = ''
            else if (next_id > result_id)
              ans.next_state = 'r-' + (next_id - 1)
          }
        })
      })

    })
  }
}
</script>

<style scoped>
.btn {
  margin-right: 5px;
}
</style>