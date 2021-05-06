<template>
  <page-header img="services" title="Настройки">
    Выберите сценарии самодиагностики, которые будут отображаться у пациента
  </page-header>

  <algorithm-selector mode="admin"
                      ref="selector"
                      :enabled="this.recommendations"></algorithm-selector>

  <!-- Кнопка добавления -->
  <div class="container">
    <button class="btn btn-block btn-outline-info"
            @click="create_algorithm()">
      Создать сценарий самодиагностики
    </button>
  </div>

  <!-- Кнопка сохранения -->
  <div class="container">
    <button class="btn btn-block btn-info"
            :disabled="!changed"
            @click="save()">Сохранить
    </button>
  </div>

</template>

<script>
import PageHeader from "../common/PageHeader";
import AlgorithmSelector from "../common/AlgorithmSelector";

export default {
  name: "SettingsPage",
  components: {AlgorithmSelector, PageHeader},
  props: ['enabled'],
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
        if (this.selector.recommendations[i])
          lst.push(this.selector.cur_algorithms[i].id)
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
      algorithms: [],
      recommendations: [],
      selection: null
    }
  },
  created() {
    this.algorithms = this.get_algorithms()
    this.recommendations = this.algorithms.map(alg => this.enabled.includes(alg.id))
    this.selection = this.$refs.selector.model
  },
  mounted() {
    Event.listen('settings-changed', () => this.changed = true)
  }
}
</script>

<style scoped>
.container {
  margin-top: 15px;
}
</style>