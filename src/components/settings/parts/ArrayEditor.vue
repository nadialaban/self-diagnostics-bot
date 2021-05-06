<template>
  <div class="container">
    <h5>{{ title }}</h5>
    <label>Кнопка будет закрашена, если все поля внутри заполнены корректно</label>

    <div class="container" v-for="(object, i) in objects">
      <div class="btn-group d-flex" role="group">
        <button class="btn btn-block text-left" data-toggle="collapse" aria-expanded="false"
                :class="errors[i] && this.validate(type, object) ? 'btn-secondary' : 'btn-outline-danger'"
                :data-target="'#collapse-' + type + '-' + object.id" :aria-controls="'collapse-' + type + '-' + object.id">
          {{ (type == 'q' ? 'Вопрос ' : 'Исход ') + object.id }}. {{ object.description }}
        </button>

        <button class="col-1 btn btn-outline-secondary" aria-label="Close"
                v-if="objects.length > 1"
                @click="del(object.id)">
          <span aria-hidden="true">&times;</span>
        </button>

        <!-- Карточка внутри -->

        <div class="collapse" v-bind:id="'collapse-' + type + '-' + object.id">
          <div class="card card-body">
            <question-editor v-if="type == 'q'" :data="object"
                             :results="results" :algorithms="algorithms" :questions="objects"
                             :errors="errors[i]"></question-editor>

            <result-editor v-if="type == 'r'" :data="object"
                           :errors="errors[i]"></result-editor>
          </div>
        </div>

      </div>
    </div>

    <!-- Кнопки добавления для вопросов -->
    <div v-if="type == 'q'" class="btn-group">
      <button class="btn btn-outline-info" @click="add_question(true)">
        Добавить вопрос в начало
      </button>
      <button class="btn btn-outline-info" @click="add_question(false)">
        Добавить вопрос в конец
      </button>
    </div>

    <!-- Кнопка добавления для исходов -->
    <button class="btn btn-outline-info" @click="add_result()" style="margin-top: 5px;">
      Добавить исход
    </button>


  </div>
</template>

<script>
import QuestionEditor from "./QuestionEditor";
import ResultEditor from "./ResultEditor";

export default {
  name: "ArrayEditor",
  components: {ResultEditor, QuestionEditor},
  props: ['data', 'title', 'type', 'results', 'algorithms', 'errors'],
  methods: {
    validate: function (type, obj) {
      switch (type) {
        case 'q':
          let validate_answers = (answer) => {
            if (!answer.answer || answer.answer == 0) return true;
            if (!answer.next_state) return true;
          }

          if (this.obj.answers.filter(validate_answers).length > 0) {
            return false
          }

          return obj.description && obj.icon;
        case 'r':
          return obj.title && obj.description && obj.color &&
              (obj.need_warn && obj.message || !obj.need_warn);
      }
    },
    del: function (object_id) {
      this.objects.splice(object_id - 1, 1)
      this.errors.splice(object_id - 1, 1)

      this.objects = this.objects.map(obj => {
        if (obj.id > object_id)
          obj.id--
      })

      if (this.type == 'q') {
        this.objects = this.objects.map(obj => {
          obj.answers = obj.answers.map(ans => {
            if (ans.next_state.startsWith('q')) {
              let next_id = parseInt(ans.next_state.split('-')[1])
              if (next_id == object_id)
                ans.next_state = ''
              else if (next_id > object_id)
                ans.next_state = 'q-' + (next_id - 1)
            }
          })
        })
      } else {
        Event.fire('delete-result', object_id)
      }
    },
    add_question: function (first) {
      if (first) {
        let q = this.get_empty_question(1)
        this.errors.unshift(this.get_question_errors())
        this.objects.unshift(q)

        this.objects = this.objects.map(obj => {
          obj.answers = obj.answers.map(ans => {
            if (ans.next_state.startsWith('q'))
              ans.next_state = 'q-' + (parseInt(ans.next_state.split('-')[1]) + 1)
          })
        })
      } else {
        let q = this.get_empty_question(this.objects.length + 1)
        this.objects.push(q)
        this.errors.push(this.get_question_errors())
      }
    },
    add_result: function () {
      let r = this.get_empty_result(this.objects.length + 1)
      this.objects.push(r)
      this.errors.push(this.get_result_errors())
    }
  },
  data() {
    return {
      objects: []
    }
  },
  created() {
    this.objects = this.data
  }
}
</script>

<style scoped>
.btn-group {
  margin-left: -15px;
  margin-right: -15px;
  margin-top: 5px;
}

.container {
  margin-top: 15px;
}
</style>