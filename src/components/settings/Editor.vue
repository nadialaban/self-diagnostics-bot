<template>
  <div>
    <page-header img="edit"
                 :title="(this.action.startsWith('create') ? 'Создание' : 'Редактирование') + ' алгоритма'"></page-header>

    <!-- Общая информация -->

    <div class="row">
      <!-- Название -->
      <field title="Название" col="6" :error="errors.title">
        <input type="text" class="form-control"
               :class="!this.empty(errors.title) && (this.empty(algorithm.title) || algorithm_exists()) ? 'is-invalid' : ''"
               placeholder="Введите название сценария самодиагностики"
               v-model="algorithm.title">
      </field>

      <!-- Иконка -->
      <field title="Иконка" col="4" :error="errors.icon">
        <select class="custom-select"
                :class="!this.empty(errors.icon) && this.empty(algorithm.icon) ? 'is-invalid' : ''"
                v-model="algorithm.icon">
          <option selected disabled value="">Выберите иконку</option>
          <option v-for="icon in icons.symptoms" :value="icon.file_name"
                  :data-thumbnail="img_url('grey', icon.file_name)">
            {{ icon.description }}
          </option>
        </select>
      </field>

      <div class="text-center col-2" style="margin-top: 25px;">
        <img v-if="algorithm.icon" :src="img_url('grey', algorithm.icon)" width="60px">
      </div>
    </div>

    <!-- Описание для пациента -->
    <field title="Описание для пациента" :error="errors.patient_description">
    <textarea class="form-control text-justify" rows="5"
              :class="!this.empty(errors.patient_description) && this.empty(algorithm.patient_description) ? 'is-invalid' : ''"
              placeholder="Введите описание сценария самодиагностики для пациента"
              v-model="algorithm.patient_description"></textarea>
    </field>

    <!-- Описание для врача -->
    <field title="Описание для врача" :error="errors.doctor_description">
    <textarea class="form-control text-justify" rows="5"
              :class="!this.empty(errors.doctor_description) && this.empty(algorithm.doctor_description) ? 'is-invalid' : ''"
              placeholder="Введите описание сценария самодиагностики для врача"
              v-model="algorithm.doctor_description"></textarea>
    </field>

    <!-- Вопросы -->
    <array-editor title="Вопросы" type="q"
                  :icons="this.icons"
                  :objects="algorithm.questions"
                  :results="algorithm.results" :algorithms="algorithms"
                  :errors="errors.questions" :algorithm_id="algorithm.id"></array-editor>

    <!-- Исходы -->
    <array-editor title="Исходы" type="r"
                  :icons="this.icons"
                  :objects="algorithm.results"
                  :errors="errors.results"></array-editor>

    <!-- Ключевые слова -->
    <field title="Ключевые слова и фразы">
    <textarea class="form-control text-justify" rows="5"
              :placeholder="'Вводите ключевые фразы с новой строчки.\n' +
              'Интеллектуальный агент будет искать их в сообщении пациента, чтобы предложить пройти этот сценарий.'"
              v-model="algorithm.keywords"></textarea>
    </field>

    <error-block :errors="warning ? [warning] : []"></error-block>

    <!-- Кнопка сохранения -->
    <button class="btn btn-block btn-info"
            :disabled="submitted"
            @click="save_algorithm()">Сохранить
    </button>

    <!-- Кнопка удаления -->
    <button class="btn btn-block btn-secondary"
            v-if="this.action.startsWith('edit') && !algorithm.depends"
            :disabled="submitted"
            @click="delete_algorithm()">Удалить
    </button>

    <!-- Кнопка возвращения -->
    <button class="btn btn-block btn-outline-info"
            :disabled="submitted"
            @click="go_back()">Вернуться
    </button>
  </div>
</template>

<script>
import PageHeader from "../common/PageHeader";
import Field from "./parts/Field";
import ArrayEditor from "./parts/ArrayEditor";
import ErrorBlock from "../common/ErrorBlock";

export default {
  name: "Editor",
  components: {ErrorBlock, ArrayEditor, Field, PageHeader},
  props: ['data', 'action', 'algorithms', 'icons'],
  methods: {
    algorithm_exists: function () {
      return this.algorithms.find(alg => alg.title == this.algorithm.title && alg.id != this.algorithm.id)
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
        icon: '',
        q_key: 1,
        r_key: 1
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
    delete_object: function (index, type) {
      let arr = {}
      switch (type) {
        case 'r':
          arr = this.algorithm.results
          this.errors.results.splice(index, 1)
          break
        case 'q':
          arr = this.algorithm.questions
          this.errors.questions.splice(index, 1)
          break
      }

      let id = arr.splice(index, 1)[0].id
      for (let i = index; i < this.algorithm.results.length; i++)
        arr[i].id--
      console.log('deleted object id', id)

      for (let i = 0; i < this.algorithm.questions.length; i++) {
        for (let j = 0; j < this.algorithm.questions[i].answers.length; j++) {
          if (this.algorithm.questions[i].answers[j].next_state.startsWith(type)) {
            let next_id = parseInt(this.algorithm.questions[i].answers[j].next_state.split('-')[1])
            if (next_id == id)
              this.algorithm.questions[i].answers[j].next_state = ''
            if (next_id > id)
              this.algorithm.questions[i].answers[j].next_state = type + '-' + (next_id - 1)
          }
        }
      }
    },
    save_algorithm: function () {
      this.submitted = true
      if (this.validate()) {
        for (let i = 0; i < this.algorithm.questions.length; i++) {
          for (let j = 0; j < this.algorithm.questions[i].answers.length; j++) {
            if (this.algorithm.questions[i].answers[j].next_state.startsWith('a')) {
              let alg_id = parseInt(this.algorithm.questions[i].answers[j].next_state.split('-')[1])
              this.algorithm.depended_algorithms.push(alg_id)
            }
          }
        }

        this.axios.post(this.url('/api/settings/save_algorithm'), this.algorithm)
            .then(r => Event.fire('save-algorithm'));
      } else {
        this.warning = 'Проверьте корректность заполнения полей!'
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
        this.errors.questions[i].description = this.empty(this.algorithm.questions[i].description) ? required : ''
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

      for (let i = 0; i < this.algorithm.results.length; i++) {
        this.errors.results[i].title = this.empty(this.algorithm.results[i].title) ? required : ''
        this.errors.results[i].description = this.empty(this.algorithm.results[i].description) ? required : ''
        this.errors.results[i].icon = this.empty(this.algorithm.results[i].icon) ? required : ''
        this.errors.results[i].color = this.empty(this.algorithm.results[i].color) ? required : ''
        this.errors.results[i].message = this.algorithm.results[i].need_warn && this.empty(this.algorithm.results[i].message) ? required : ''

        if (this.errors.results[i].title || this.errors.results[i].description ||
            this.errors.results[i].color || this.errors.results[i].icon ||
            this.errors.results[i].need_warn && this.errors.results[i].message)
          flag = true

      }

      return !(flag || this.errors.title || this.errors.icon ||
          this.errors.patient_description || this.errors.doctor_description);
    },
    add_question: function (first) {
      let len = this.algorithm.questions.length
      if (first) {
        let q = this.get_empty_question(1, len)
        this.errors.questions.unshift(this.get_question_errors())
        this.algorithm.questions.unshift(q)

        for (let i = 1; i < len; i++) {
          this.algorithm.questions[i].id++
          for (let j = 0; j < this.algorithm.questions[i].answers.length; j++) {
            if (this.algorithm.questions[i].answers[j].next_state.startsWith('q')) {
              let next_id = parseInt(this.algorithm.questions[i].answers[j].next_state.split('-')[1])
              this.algorithm.questions[i].answers[j].next_state = 'q-' + (next_id + 1)
            }
          }
        }
      } else {
        this.algorithm.questions.push(this.get_empty_question(len + 1, len))
        this.errors.questions.push(this.get_question_errors())
      }
    },
    add_result: function () {
      let len = this.algorithm.results.length
      this.algorithm.results.push(this.get_empty_result(len + 1, len))
      this.errors.results.push(this.get_result_errors())

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
            Event.fire('back-to-settings')
          }
        }
      })
    }
  },
  data() {
    return {
      errors: {},
      algorithm: {},
      submitted: false,
      warning: ''
    }
  },
  created() {
    this.algorithm = this.data

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

    Event.listen('add-question', data => this.add_question(data))
    Event.listen('add-result', () => this.add_result())

    Event.listen('delete-result', result_index => this.delete_object(result_index, 'r'))
    Event.listen('delete-question', question_index => this.delete_object(question_index, 'q'))
  }
}
</script>

<style scoped>
.btn {
  margin-right: 5px;
}
</style>