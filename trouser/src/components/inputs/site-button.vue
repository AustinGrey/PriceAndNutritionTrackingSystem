<!--
The typical button used on the site. Has props to allow changing between what type of button is primary
-->
<template>
    <button
            :id="id"
            :class="[$options.name, {primary: primary}]"
            @click="$emit('click')"
            :disabled="disabled"
    >
        <slot></slot>
    </button>
</template>

<script>
    export default {
        name: "site-button",
        props: {
            id: String,
            primary: {type: Boolean, default: false},
            onClick: Function,
            disabled: {type: Boolean, default: false},
        }
    }
</script>

<style scoped lang="scss">
    @import 'src/assets/css/_colors.scss';

    button {
        border-radius: var(--border-radius);

        // Keep everything on one line
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;

        padding: var(--padding-thin);

        background: c(button, background);
        border: 1px solid c(button, border);
        color: c(button, font);

        &[disabled]{
            background: c(button-disabled, background);
            border-color: c(button-disabled, border);
            color: c(button-disabled, font);
        }

        &.primary{
            background: c(button-primary, background);
            border-color: c(button-primary, border);
            color: c(button-primary, font);

            // Why would a button be both primary, and disabled?
            &[disabled]{
                background: c(button-primary-disabled, background);
                border-color: c(button-primary-disabled, border);
                color: c(button-primary-disabled, font);
            }
        }

        &.dark {

            &:hover {
                color: var(--shamrock-green);
            }

            &:active {
                box-shadow: inset 0 0 0.5em var(--pine-green);
            }
        }

        &.text-only {
            border: 0;
            padding: 0;
            color: var(--shamrock-green);
            background: #0000;

            &:hover {
                color: var(--pine-green);
            }
        }
    }
</style>