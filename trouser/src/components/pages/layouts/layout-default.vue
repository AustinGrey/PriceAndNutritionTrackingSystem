<template>
    <div :class="$options.name">
        <div class="menu">
            <div class="nav">
                <router-link
                        v-for="(item, key) in menu_items"
                        :key="key"
                        :to="item.url"
                        class="nav-item"
                        :class="{active: currentLoc === key}"
                >
                    <fa-icon :icon="['fas', item.icon]"></fa-icon>
                </router-link>
            </div>
        </div>
        <div class="quick-info">
            <h1 class="page-title">
                <slot name="page_title"></slot>
            </h1>
            <slot name="quick_info"></slot>
        </div>
        <div class="content">
            <slot name="content"></slot>
        </div>
    </div>
</template>

<script>
    export default {
        name: "layout-default",
        props: {
            currentLoc: {
                type: String
            },
            menu_items: {
                type: Object,
                required: true
            }
        }
    }
</script>

<style scoped lang="scss">
    @import "../../../assets/css/responsive";

    // Mobile first design, xs screen sizes defined first
    .layout-default {
        height: 100vh; // We take control of the layout entirely, and decide what scrolls when
        display: grid;
        grid-template-columns: 1fr;
        // Right now the 'quick info' section is unused, unsure if I want to remove it, or utilize it.
        grid-template-rows: 0 1fr var(--menu-width);
        grid-template-areas: "quick-info" "content" "menu";

        .quick-info {
            grid-area: quick-info;
            padding: var(--padding);
            display: flex;
            align-items: center;
        }

        .content {
            grid-area: content;
            padding: var(--padding);
            overflow: auto;
        }

        .menu {
            grid-area: menu;

            background: var(--gunmetal);
            color: var(--pine-green);

            > .nav {
                top: 0;
                display: flex;
                flex-direction: row;
                justify-content: space-between;

                > .nav-item {
                    width: var(--menu-width);
                    height: var(--menu-width);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    color: var(--pine-green);
                    position: relative;

                    &:visited{
                        color: var(--pine-green);
                    }

                    &.router-link-exact-active::after{
                        content: "";
                        width: 0;
                        height: 0;
                        border-left: 0.5em solid transparent;
                        border-top: 1em solid var(--shamrock-green);
                        border-right: 0.5em solid transparent;
                        position: absolute;
                        top: -0.2em;
                    }

                    > svg{
                        font-size: calc(var(--menu-width) / 2);
                    }
                }
            }

            .spacer {
                flex: 1;
            }
        }
    }

    @include breakpoint-from(md) {
        .layout-default {
            grid-template-columns: var(--menu-width) 1fr;
            // Right now the 'quick info' section is unused, unsure if I want to remove it, or utilize it.
            grid-template-rows: 0 1fr;
            grid-template-areas: "menu quick-info" "menu content";

            .quick-info {
                padding: var(--padding);
                display: flex;
                align-items: center;
            }

            .menu{
                >.nav {
                    flex-direction: column;
                    justify-content: flex-start;
                    height: 100vh;

                    > .nav-item {
                        &.router-link-exact-active::after{
                            border-top: 0.5em solid transparent;
                            border-right: 1em solid var(--shamrock-green);
                            border-bottom: 0.5em solid transparent;
                            top: unset;
                            right: -0.2em;
                        }
                    }
                }
            }
        }
    }
</style>

<style lang="scss">
    @import url('https://fonts.googleapis.com/css2?family=Quicksand&family=Raleway&display=swap');
    @import "./src/assets/css/responsive";


    /* Layout/Typography */
    :root {
        --menu-width: 3em;

        --font-family-headings: 'Quicksand', sans-serif;
        --font-family-content: 'Raleway', sans-serif;

        --padding: 1em;
        --padding-thin: 0.5em;
        --border-radius: 4px;

        font-family: var(--font-family-content);
    }

    body {
        margin: 0;
        background: var(--baby-powder);
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: var(--font-family-headings);
        margin-top: 0.5em;
        margin-bottom: 0.25em;
    }

    h1 {
        font-size: 2em;
    }

    h2 {
        font-size: 1.5em;
    }

    h3 {
        font-size: 1.25em;
    }

    /* Flex Utilties */
    /* @todo extract these into sass mixins instead */
    .flex-row-start {
        display: flex;
        flex-direction: row;
        justify-content: flex-start;
        align-items: center;
    }

    .flex-row-between {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
    }

    .flex-row_r-between {
        display: flex;
        flex-direction: row-reverse;
        justify-content: space-between;
        align-items: center;
    }

    .flex-gap-regular {
        gap: var(--padding);
    }

    .flex-row-equalfill {
        display: flex;
        flex-direction: row;
        align-items: center;
    }

    .flex-row-equalfill > * {
        flex: 1;
    }


    /* Colors */
    /* @todo keep these specific colors, but also specify semantic colors that use these for semantic consistency */
    :root {
        --gunmetal: hsla(227, 15%, 24%, 1);
        --baby-powder: hsla(100, 100%, 99%, 1);
        --pine-green: hsla(173, 71%, 28%, 1);
        --shamrock-green: hsla(142, 37%, 45%, 1);
        --brown-sugar: hsla(15, 42%, 50%, 1);
    }

    /* Quick Info */
    .quick-info .page-title {
        margin: 0;
    }



    /* Inputs */
    /* @todo move this to the float input component */
    input:focus, textarea:focus {
        box-shadow: inset 0 0 1px var(--shamrock-green);
    }

    button {
        border-radius: var(--border-radius);
        border: 1px solid black;
    }

    button.oneline {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    button.dark {
        background: var(--gunmetal);
        color: var(--pine-green);
        font-weight: bold;
        border-color: var(--pine-green);
        padding: var(--padding-thin);
    }

    button.dark:hover {
        color: var(--shamrock-green);
    }

    button.dark:active {
        box-shadow: inset 0 0 0.5em var(--pine-green);
    }

    button.text-only {
        border: 0;
        padding: 0;
        color: var(--shamrock-green);
        background: #0000;
    }

    button.text-only:hover {
        color: var(--pine-green);
    }

    @include breakpoint-from(md){
        :root{
            --menu-width: 5em;
        }
    }
</style>


