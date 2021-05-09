<template>
  <div>

    <page-header img="services" title="Настройки">
      Выберите сценарии самодиагностики, которые будут отображаться у пациента
    </page-header>

    <loading v-if="!updated"></loading>
    <algorithm-selector v-else mode="admin"
                        :algorithms="algorithms"
                        :editable="editable"
                        :recommendations="recommendations"></algorithm-selector>

    <!-- Кнопка добавления -->
    <button class="btn btn-block btn-outline-info"
            @click="create_algorithm()">
      Создать сценарий самодиагностики
    </button>

    <!-- Кнопка сохранения -->
    <button class="btn btn-block btn-info"
            :disabled="!changed" @click="save()">Сохранить
    </button>
  </div>
</template>

<script>
import PageHeader from "../common/PageHeader";
import AlgorithmSelector from "../common/AlgorithmSelector";
import Loading from "../Loading";

export default {
  name: "SettingsPage",
  components: {Loading, AlgorithmSelector, PageHeader},
  props: {
    enabled: {
      required: true
    },
    algorithms: {
      required: true
    }
  },
  methods: {
    create_algorithm: function () {
      if (this.changed) {
        this.$confirm({
          message: `Вы уверены? Все несохраненные данные будут утеряны!`,
          button: {
            no: 'Нет',
            yes: 'Да'
          },
          callback: confirm => {
            if (confirm) {
              Event.fire('create-algorithm')
            }
          }
        })
      } else {
        Event.fire('create-algorithm')
      }
    },
    save: function () {
      this.submitted = true

      let lst = [];

      for (let i = 0; i < this.recommendations.length; i++) {
        if (this.recommendations[i])
          lst.push(this.algorithms[i].id)
      }

      let data = {
        'recommendations': lst
      }

      this.axios.post(this.url('/api/settings/save'), data)
          .then(r => Event.fire('settings-set'))
          .catch(() => {
            this.errors = ['Произошла ошибка сохранения']
            this.submitted = false
          });
    }
  },
  data() {
    return {
      submitted: false,
      changed: false,
      updated: false,
      recommendations: null,
      editable: null,
      selection: null
    }
  },
  created() {
    this.updated = false

    this.recommendations = this.algorithms.map(alg => this.enabled.includes(alg.id))
    this.editable = this.algorithms.map(alg => this.clinic_id == alg.clinic_id)
    this.updated = true

    Event.listen('settings-changed', (data) => {
      this.changed = true
      this.recommendations[data.index] = data.value
      console.log(this.recommendations)
    });
  }
}
</script>

<style scoped>
.container {
  margin-top: 15px;
}
</style>