<template>
    <div class="card">
        <header class="card-header">
            <p class="card-header-title">
                {{ film.title }}
            </p>
        </header>
        <div class="card-image">
            <figure>
                <img :src="film.img_url || 'placeholder-image.jpg'" alt="Film Image">
            </figure>
        </div>
        <div class="card-content">
            <div class="content">
                {{ film.oneliner }}
            </div>
        </div>
        <footer class="card-footer">
            <a :href="film.slug" class="card-footer-item">Cineville</a>
            <a :href="film.clean_title" class="card-footer-item">Letterboxd</a>
            <a :href="tmdb_id" class="card-footer-item">IMDb</a>
            <a :href="imdb_id" class="card-footer-item">TMDB</a>
        </footer>
    </div>
</template>

<script>
export default {
    props: ['film'],
};
</script>