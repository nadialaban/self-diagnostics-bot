<template>
  <field title="Заголовок" :error="errors.title">
    <input type="text" class="form-control"
           :class="!this.empty(errors.title) && this.empty(result.title)? 'is-invalid' : ''"
           placeholder="Введите заголовок исхода"
           v-model="result.title">
  </field>

  <div class="row">
    <field title="Иконка" col="4" :error="errors.icon">
      <select class="custom-select" v-model="result.icon"
              :class="!this.empty(errors.icon) && this.empty(result.icon) ? 'is-invalid' : ''">
        <option selected disabled value="">Выберите иконку</option>
        <option v-for="icon in this.icons.symptoms" :value="icon.file_name"
                :data-thumbnail="this.img_url('grey', icon.file_name)">
          {{ icon.description }}
        </option>
      </select>
    </field>

    <field title="Цвет" col="4" :error="errors.color">
      <select class="custom-select"
              :class="!this.empty(errors.color) && this.empty(result.color) ? 'is-invalid' : ''">
        v-model="result.color">
        <option selected disabled value="">Выберите цвет...</option>
        <option value="grey">Серый</option>
        <option value="green">Зеленый</option>
        <option value="yellow">Желтый</option>
        <option value="red">Красный</option>
      </select>
    </field>

    <div class="text-center col-2" style="margin-top: 25px;">
      <img v-show="result.icon" :src="this.img_url(result.color, result.icon)" width="60px">
    </div>
  </div>

  <field title="Описание" :error="errors.description">
        <textarea class="form-control text-justify" rows="4"
                  placeholder="Введите описание проблемы и инструкции для пациента"
                  :class="!this.empty(errors.description) && this.empty(result.description) ? 'is-invalid' : ''"
                  v-model="result.description"></textarea>
  </field>

  <div class="custom-control custom-checkbox mb-3">
    <input class="form-check-input" type="checkbox"
           id="need_warn" v-model="result.need_warn">
    <label for="need_warn">Сообщать врачу</label>
  </div>

  <div v-if="result.need_warn" class="container">
    <field title="Сообщение для врача" :error="errors.message">
        <textarea class="form-control text-justify" rows="4"
                  placeholder="Введите текст сообщения, которое будет отправлено врачу"
                  :class="!this.empty(errors.message) && this.empty(result.message) ? 'is-invalid' : ''"
                  v-model="result.message"></textarea>
    </field>

    <div class="custom-control custom-checkbox mb-3">
      <input class="form-check-input" type="checkbox"
             id="need_response" v-model="result.need_response">
      <label for="need_warn">Требовать реакцию врача</label>
    </div>
  </div>

</template>

<script>
import Field from "./Field";

export default {
  name: "ResultEditor",
  components: {Field},
  props: ['data', 'errors'],
  data() {
    return {
      result: {},
      result_errors: []
    }
  },
  created() {
    this.result = this.data
    this.result_errors = this.errors
  }
}
</script>

<style scoped>
.custom-control {
  margin-top: 15px;
  margin-left: 15px;
}
</style>