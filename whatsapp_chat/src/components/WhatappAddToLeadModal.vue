<template>
  <Dialog v-model="show" :options="{ title: `Add ${form_name}`, size: '2xl' }">
    <template #body-content>
        <div
          v-for="(field, index) in dynamicFields"
          :key="index"
          class="p-2"
          :class="{ 'overflow-y-auto max-h-96': dynamicFields.length > 8 }"
        >
          <FormControl
            :type="mapInputType(field.doctype_field_type, field.lead_field_name)"
            :size="'sm'"
            :variant="'subtle'"
            :placeholder="field.lead_field_name"
            :label="formatLabel(field.lead_field_name)"
            v-model="lead[field.lead_field_name]"
            :options="getOptions(field)"
            :as="mapInputType(field.doctype_field_type, field.lead_field_name) === 'autocomplete' ? 'autocomplete' : null"
          />
        </div>
        <div class="mt-4 flex justify-end text-black">
          <Button label="Cancel" class="mr-2" type="button" @click="closeDialog" />
          <Button variant="solid" theme="gray" size="sm" type="button" label="Save Lead" @click.prevent="submitLead" />
        </div>
    </template>
  </Dialog>
</template>



<script setup>
import { ref, watchEffect, defineProps } from "vue";
import { Button, FormControl, createResource } from "frappe-ui";
import { toRaw } from "vue";

const props = defineProps({
  contact_number: String,
  first_name: String,
});

const show = ref(true);
const responseMessage = ref("");

const fieldMappingsResource = createResource({
  url: "/api/method/frappe_whatsapp.api.whatsapp.get_leadmapping_fields",
  auto: true,
});

const formDataResource = createResource({
  url: "/api/method/frappe_whatsapp.api.whatsapp.get_form_data",
  auto: true,
});

const executiveOptions = ref([]);
const centerOptions = ref([]);
const dynamicFields = ref([]);
const lead = ref({});
const form_name = ref("");
const response = ref("");

// Watch effect to populate form fields
watchEffect(() => {
  if (formDataResource.data?.message) {
    executiveOptions.value =
      formDataResource.data.message.executive?.map((exec) => ({
        label: exec,
        value: exec,
      })) || [];

    centerOptions.value =
      formDataResource.data.message.center?.map((center) => ({
        label: center,
        value: center,
      })) || [];
  }
});

watchEffect(() => {
  if (fieldMappingsResource.data?.field_mappings) {
    dynamicFields.value = fieldMappingsResource.data.field_mappings;
    form_name.value = fieldMappingsResource.data.mappings.lead_reference_doctype;
    
    lead.value = dynamicFields.value.reduce((acc, field) => {
      acc[field.lead_field_name] = field.lead_field_name === "source" ? "Whatsapp" : "";
      return acc;
    }, {});

    lead.value.contact_number = props.contact_number || "Dummy";
    lead.value.first_name = props.first_name || "123456";
    lead.value.created_on = new Date().toISOString().split('T')[0];
  }
});

// Function to close the modal
const closeDialog = () => {
  show.value = false;
  console.log("Closing modal, show =", show.value);
};

// Function to map field types
const mapInputType = (doctypeFieldType, leadFieldValue) => {
  if (leadFieldValue === "created_on") {
    return "text"; // Explicitly setting 'created_on' as text
  }

  const typeMap = {
    Data: "text",
    Phone: "tel",
    Date: "text",
    Select: "autocomplete",
    Link: "autocomplete",
  };
  
  return typeMap[doctypeFieldType] || "text";
};

// Format field label
const formatLabel = (key) => {
  return key.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
};

// Get field options
const getOptions = (field) => {
  if (field.doctype_field_type === "Select") {
    return field.select_options.map((option) => ({ label: option, value: option }));
  } else if (field.doctype_field_type === "Link") {
    return field.linked_records.map((record) => ({ label: record, value: record }));
  }
  return [];
};

// Submit form data
const submitLead = async () => {
  const leadData = JSON.parse(JSON.stringify(toRaw(lead.value)));
  const doctype = JSON.parse(JSON.stringify(toRaw(form_name.value)));

  try {
    const response = await fetch("/api/method/frappe_whatsapp.api.whatsapp.save_as_lead", {
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      method: "POST",
      body: JSON.stringify({
        doctype: doctype,
        data: leadData,
      }),
    });

    const result = await response.json();
    console.log("Lead Submitted:", result);
  } catch (error) {
    console.error("Error submitting lead:", error);
  }
};
</script>
