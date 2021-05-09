<template>
  <div style="margin-top: 20px;">
    <h5>{{ title }}</h5>
    <label>Кнопка будет закрашена, если все поля внутри заполнены корректно</label>

    <div v-for="(object, i) in objects" :key="object.key">
      <div class="btn-group d-flex" role="group">
        <button class="btn text-left" data-toggle="collapse" aria-expanded="false"
                :class="errors[i] && validate(object) ? (type == 'r'? get_button_color(object.color) : 'btn-secondary') : 'btn-outline-danger'"
                :data-target="'#collapse-' + type + '-' + object.id" :aria-controls="'collapse-' + type + '-' + object.id">
          {{ (type == 'q' ? 'Вопрос ' : 'Исход ') + object.id }}. {{ type == 'q' ? object.description : object.title }}
        </button>

        <button class="col-1 btn btn-outline-secondary" aria-label="Close"
                v-if="objects.length > 1" @click="del(i)">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>

      <!-- Карточка внутри -->

      <div class="collapse" v-bind:id="'collapse-' + type + '-' + object.id">
        <div class="card card-body">
          <question-editor v-if="type == 'q'" :data="object" :icons="icons"
                           :results="results" :algorithms="algorithms" :questions="objects"
                           :errors="errors[i]"></question-editor>

          <result-editor v-if="type == 'r'" :data="object" :icons="icons"
                         :errors="errors[i]"></result-editor>
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
    <button v-if="type == 'r'" class="btn btn-outline-info" @click="add_result()" style="margin-top: 5px;">
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
  props: ['objects', 'title', 'type', 'results', 'algorithms', 'errors', 'icons', 'algorithm_id'],
  methods: {
    validate: function (obj) {
      switch (this.type) {
        case 'q':
          let validate_answers = (answer) => {
            if (!answer.answer || answer.answer == 0) return true;
            if (!answer.next_state) return true;
          }

          if (obj.answers.filter(validate_answers).length > 0) {
            return false
          }

          return obj.description && obj.icon;
        case 'r':
          return obj.title && obj.description && obj.color &&
              (obj.need_warn && obj.message || !obj.need_warn);
      }
    },
    del: function (index) {
      switch (this.type) {
        case 'q':
          Event.fire('delete-question', index)
          break
        case 'r':
          Event.fire('delete-result', index)
          break
      }
    },
    add_question: function (first) {
      Event.fire('add-question', first)
    },
    add_result: function () {
      Event.fire('add-result')
    },
    get_button_color: function (color) {
      switch (color) {
        case 'grey':
          return 'btn-secondary';
        case 'green':
          return 'btn-success';
        case 'yellow':
          return 'btn-warning';
        case 'red':
          return 'btn-danger';
      }
    }
  }
}
</script>

<style scoped>
.btn-group {
  margin-top: 5px;
}

.container {
  margin-top: 15px;
}
</style>