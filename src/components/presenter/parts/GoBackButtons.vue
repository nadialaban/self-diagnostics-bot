<template>
  <div>
    <div class="btn-group d-flex">
      <button class="btn btn-block btn-outline-info"
              @click="fire_event('back-to-menu')">К началу
      </button>
      <button class="btn btn-block btn-outline-info"
              v-if="history.length"
              @click="fire_event(loc == 'res' ? 'back-to-test' : 'previous-question')">Предыдущий вопрос
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: "GoBackButtons",
  props: ['history', 'algorithm', 'loc'],
  methods: {
    fire_event: function (event) {
      let data = {}
      if (!this.history.length) {
        Event.fire('back-to-menu');
      } else if (event == 'back-to-menu') {
        this.$confirm({
          message: `Вы уверены? Ваши ответы будут утрачены!`,
          button: {
            no: 'Нет',
            yes: 'Да'
          },
          callback: confirm => {
            if (confirm) {
              Event.fire(event)
            }
          }
        })
      } else {
        data = {
          history: this.history,
          algorithm: this.algorithm,
          handled: false
        }
        Event.fire(event, data);
      }
    }
  }
}
</script>

<style scoped>
.btn-group {
  margin-top: 5px;
}

.btn {
  margin-top: 15px;
}
</style>