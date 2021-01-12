<!-- For when using an input-float, but not using the automatic labelling so you can position the label wherever you like -->
<template>
    <label
            :class="$options.name"
            :for="_for"
    >
        {{content}}
        <slot v-if="!content"></slot>
    </label>
</template>

<script>
    export default {
        name: "input-label",
        props: {
            // The ID of the input-float this label is for
            _for: {
                type: String,
                default: ""
            },
            // What to put into the label. Overrides the slot if used
            content: {
                type: String,
                default: ""
            }
        }
    }
</script>

<style scoped>
</style>