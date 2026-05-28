<template>
  <section class="panel selected-panel">
    <header class="panel-header">
      <div>
        <p class="eyebrow">{{ eyebrow }}</p>
        <h2>{{ title }}</h2>
      </div>
      <span class="selected-summary">Checked {{ checkedCount }} / {{ totalCount }} {{ summaryLabel }}</span>
    </header>

    <div v-if="showToolbar" class="selected-toolbar">
      <div class="select-all">
        <div class="select-all-control">
          <input
            type="checkbox"
            :checked="allSelected"
            :indeterminate="partiallySelected"
            :disabled="totalCount === 0"
            @change="$emit('toggle-all', $event.target.checked)"
          />
          <span>Select all</span>
        </div>
        <div class="delete-all-control">
          <span>Delete all</span>
          <button
            class="delete-all-button"
            type="button"
            aria-label="Delete all selected items"
            :disabled="totalCount === 0"
            @click="$emit('delete-all')"
          >
            <svg class="delete-item-icon" viewBox="0 0 24 24" aria-hidden="true">
              <path
                d="M9 3h6l1 2h4v2H4V5h4l1-2Zm1 7v8h2v-8h-2Zm4 0v8h2v-8h-2ZM7 8h10l-1 13H8L7 8Z"
                fill="currentColor"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <div v-if="items.length === 0" class="empty-state multiline-empty-state">
      <span>{{ emptyMessage }}</span>
    </div>

    <ul v-else class="selected-list">
      <li
        v-for="item in items"
        :key="itemValue(item)"
        class="selected-item"
        :class="{ active: activeValue === itemValue(item), 'without-delete': !showDeleteButton }"
        @click="$emit('select', item)"
      >
        <div class="selected-item-check" @click.stop>
          <input
            type="checkbox"
            :checked="item.checked"
            @change="$emit('update-checked', item, $event.target.checked)"
          />
        </div>
        <div class="selected-item-scroll">
          <span class="selected-item-text" :title="itemText(item)">{{ itemText(item) }}</span>
        </div>
        <button
          v-if="showDeleteButton"
          class="delete-item-button"
          type="button"
          :aria-label="`Delete ${itemText(item)}`"
          @click.stop="$emit('delete', item)"
        >
          <svg class="delete-item-icon" viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M9 3h6l1 2h4v2H4V5h4l1-2Zm1 7v8h2v-8h-2Zm4 0v8h2v-8h-2ZM7 8h10l-1 13H8L7 8Z"
              fill="currentColor"
            />
          </svg>
        </button>
      </li>
    </ul>
  </section>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  items: {
    type: Array,
    required: true,
  },
  checkedCount: {
    type: Number,
    required: true,
  },
  totalCount: {
    type: Number,
    required: true,
  },
  activeValue: {
    type: String,
    default: "",
  },
  eyebrow: {
    type: String,
    default: "Selected",
  },
  title: {
    type: String,
    default: "Selected Items",
  },
  summaryLabel: {
    type: String,
    default: "items",
  },
  emptyMessage: {
    type: String,
    default: "No selected items.",
  },
  showToolbar: {
    type: Boolean,
    default: false,
  },
  showDeleteButton: {
    type: Boolean,
    default: true,
  },
  valueKey: {
    type: String,
    default: "path",
  },
  textKey: {
    type: String,
    default: "path",
  },
});

defineEmits(["update-checked", "toggle-all", "delete", "delete-all", "select"]);

const allSelected = computed(() => {
  return props.totalCount > 0 && props.checkedCount === props.totalCount;
});

const partiallySelected = computed(() => {
  return props.checkedCount > 0 && !allSelected.value;
});

function itemValue(item) {
  return String(item?.[props.valueKey] ?? "");
}

function itemText(item) {
  return String(item?.[props.textKey] ?? itemValue(item));
}
</script>
