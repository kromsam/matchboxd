//
document.addEventListener("DOMContentLoaded", function () {
  const lb_list_JsonURL = "data/lb_list.json";
  fetch(lb_list_JsonURL)
    .then((response) => response.json())
    .then((data) => {
      // Extract the API_URL from the JSON
      const letterboxdList = data;

      // const letterboxdList = "{{ user }}/{{ user_list }}";
      const letterboxdListURL = `https://letterboxd.com/${letterboxdList}`;

      // Create the heading text with the letterboxd_list part as a URL
      const headingText = `Films in <span id="city-content">
        <a href="#" id="city-link"></a><span id="city-dropdown" class="dropdown">
          <select id="city-select" class="form-select"></select>
        </span>
      </span> van <a href="${letterboxdListURL}" target="_blank">${letterboxdList}</a> 
      <a href="#" id="sortingText"></a>`;

      // Update the <h1> element
      const h1Element = document.querySelector("h1");
      h1Element.innerHTML = headingText;

      // Event listeners for click actions
      document
        .getElementById("city-link")
        .addEventListener("click", function (event) {
          event.preventDefault();
          toggleCityDropdown();
        });

      document
        .getElementById("sortingText")
        .addEventListener("click", function (event) {
          event.preventDefault();
          toggleSortingMode();
        });

      const sortingTextElement = document.getElementById("sortingText");

      // Set the initial value based on the sortingMode
      if (sortingMode === "film") {
        sortingTextElement.textContent = "per film";
      } else {
        sortingTextElement.textContent = "op datum";
      }

      ///

      // Get the reference to the elements
      // const cityLink = document.getElementById('city-link');
      // const cityDropdown = document.getElementById('city-dropdown');
      const citySelect = document.getElementById("city-select");

      // Function to dynamically adjust the dropdown width
      function updateDropdownWidth() {
        const selectedOption = citySelect.options[citySelect.selectedIndex];
        const textWidth = selectedOption.text.length * 8; // Adjust the factor as needed
        citySelect.style.width = `${textWidth}px`;
      }

      // Load cities from 'cities.json' and populate the dropdown
      fetch(cityjsonURL) // Adjust the URL to the path of your 'cities.json' file
        .then((response) => response.json())
        .then((data) => {
          data.forEach((city) => {
            const option = document.createElement("option");
            option.value = city;
            option.text = city;
            citySelect.appendChild(option);
          });
          // Set the selected city based on the "city" parameter in the URL
          const urlParams = new URLSearchParams(window.location.search);
          const selectedCity = urlParams.get("city");
          if (selectedCity) {
            citySelect.value = selectedCity;
            selectCity(); // Show the selected city as a link
          }
        })
        .catch((error) => console.error("Error loading cities: ", error));

      // Event listener for the dropdown change
      citySelect.addEventListener("change", function () {
        updateDropdownWidth();
        const selectedCity = citySelect.value;
        updateCityParameter(selectedCity);
      });

      // Initialize the dropdown width
      updateDropdownWidth();

      // Function to update the URL parameter and reload the page
      function updateCityParameter(selectedCity) {
        const currentURL = new URL(window.location.href);

        // Preserve other parameters by copying them from the existing URL
        const urlParams = new URLSearchParams(currentURL.search);
        urlParams.set("city", selectedCity);

        // Replace the current URL search with the updated parameters
        currentURL.search = urlParams.toString();

        // Reload the page with the updated URL
        window.location.href = currentURL.toString();
      }
    });
});
/// Global variables

let fetchedData = null;
const cityjsonURL = "data/cities.json";
const jsonURL = "data/films_with_showings.json";
const sortingMode = getSortingMode();

/// City-select functions

//
function selectCity() {
  const cityLink = document.getElementById("city-link");
  const cityDropdown = document.getElementById("city-dropdown");
  const citySelect = document.getElementById("city-select");
  const selectedCity = citySelect.value;

  cityLink.textContent = selectedCity;
  cityLink.href = "#"; // Set the URL as needed

  cityLink.style.display = "inline-block";
  cityDropdown.style.display = "none";
  citySelect.style.width = ""; // Reset the width when text is shown
}

//
function toggleCityDropdown() {
  const cityLink = document.getElementById("city-link");
  const cityDropdown = document.getElementById("city-dropdown");

  if (cityLink.style.display === "none") {
    cityLink.style.display = "inline-block";
    cityDropdown.style.display = "inline-block";
  } else {
    cityLink.style.display = "none";
    cityDropdown.style.display = "inline-block";
  }
}

/// Mode-select functions

// Parse the URL to check for the "sort" query parameter
function getSortingMode() {
  const urlParams = new URLSearchParams(window.location.search);
  let sortingMode = urlParams.get("sort");

  // Check if sortingMode is neither 'date' nor 'film', and set it to 'film' in that case
  if (sortingMode !== "date" && sortingMode !== "film") {
    sortingMode = "film";
    urlParams.set("sort", sortingMode);
    const newUrl = `${window.location.pathname}?${urlParams.toString()}`;
    window.history.replaceState(null, null, newUrl);
  }
  return sortingMode;
}

// Function to toggle sorting mode and update the URL
function toggleSortingMode() {
  // Get the current URL parameters as an object
  const urlParams = new URLSearchParams(window.location.search);

  // Check the current sorting mode
  const sortingMode = urlParams.get("sort");

  // Toggle the sorting mode
  if (sortingMode === "film") {
    urlParams.set("sort", "date");
    document.getElementById("sortingText").textContent = "op datum";
  } else {
    urlParams.set("sort", "film");
    document.getElementById("sortingText").textContent = "per film";
  }

  // Create the new URL with the updated parameters
  const newURL = `${window.location.pathname}?${urlParams.toString()}`;

  // Update the URL
  window.history.replaceState({}, document.title, newURL);

  // Call fetchDataAndRender with the updated sorting mode
  renderData(urlParams.get("sort"));
}

/// Data processing functions

//
function formatDateToDutch(dateString) {
  const options = {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  };
  return new Date(dateString).toLocaleDateString("nl-NL", options);
}

//
function getEarliestScreeningTime(film) {
  const times = film.showings
    .filter((showing) => showing.date)
    .map((showing) => showing.time_start);

  if (times.length > 0) {
    times.sort();
    return times[0];
  }

  return null;
}

//
function getFirstScreeningDate(film) {
  const screeningDates = film.showings
    .filter((showing) => showing.date)
    .map((showing) => new Date(showing.date));

  if (screeningDates.length > 0) {
    screeningDates.sort((a, b) => a - b);
    return screeningDates[0];
  }

  return null;
}

//
function groupShowingsByDateAndTheater(showings) {
  const groupedShowings = {};
  showings.forEach((showing) => {
    const date = showing.date;
    const theater = showing.location_name;
    if (!groupedShowings[date]) {
      groupedShowings[date] = {};
    }
    if (!groupedShowings[date][theater]) {
      groupedShowings[date][theater] = [];
    }
    groupedShowings[date][theater].push(showing);
  });
  return groupedShowings;
}

/// Data rendering functions

// Function to fetch and render data based on sorting mode
function fetchDataAndRender(sortingMode) {
  if (fetchedData === null) {
    // Fetch data only if it hasn't been fetched yet
    fetch(jsonURL)
      .then((response) => response.json())
      .then((data) => {
        fetchedData = data; // Store the fetched data
        renderData(sortingMode); // Render data based on sorting mode
      })
      .catch((error) =>
        console.error("Fout bij het ophalen van gegevens: ", error)
      );
  } else {
    // Data has already been fetched, just render it based on sorting mode
    renderData(sortingMode);
  }
}

//
function renderData(sortingMode) {
  // Clear the existing filmCards or dateCards
  const filmCards = document.getElementById("FilmCard");
  filmCards.innerHTML = "";

  const showingsByDate = document.getElementById("DateCard");
  showingsByDate.innerHTML = "";

  // Get the data to render (fetchedData)
  const data = fetchedData;

  if (sortingMode === "film") {
    const filmCards = document.getElementById("FilmCard");

    data.sort((a, b) => {
      const firstScreeningA = getFirstScreeningDate(a);
      const firstScreeningB = getFirstScreeningDate(b);

      if (firstScreeningA && firstScreeningB) {
        if (firstScreeningA - firstScreeningB === 0) {
          const earliestTimeA = getEarliestScreeningTime(a);
          const earliestTimeB = getEarliestScreeningTime(b);

          if (earliestTimeA && earliestTimeB) {
            return earliestTimeA.localeCompare(earliestTimeB);
          }
        }
        return firstScreeningA - firstScreeningB;
      } else if (firstScreeningA) {
        return -1;
      } else if (firstScreeningB) {
        return 1;
      }
      return 0;
    });

    data.forEach((film, index) => {
      const card = document.createElement("div");
      card.className = "col-md-4";

      const showingCount = film.showings.length;

      const showingsOrInfo = film.showings[0].date
        ? `
                      <button class="btn btn-link" data-bs-toggle="collapse" data-bs-target="#collapse-${index}">
                          Toon ${showingCount} ${
            showingCount === 1 ? "Voorstelling" : "Voorstellingen"
          }
                      </button>
                      <div class="collapse card-collapse" id="collapse-${index}">
                          <ul class="list-group list-group-flush">
                              ${Object.entries(
                                groupShowingsByDateAndTheater(film.showings)
                              )
                                .map(
                                  ([date, theaters]) => `
                                  <li class="list-group-item">
                                      <strong>${formatDateToDutch(
                                        date
                                      )}</strong>
                                      <div class="showing-details">
                                          ${Object.entries(theaters)
                                            .map(
                                              ([theater, showings]) => `
                                              <div class="showing">
                                                  <strong>${theater}</strong>
                                                  ${showings
                                                    .map(
                                                      (showing) => `
                                                      <div class="showing-item">
                                                          ${
                                                            showing.additional_info
                                                              ? `<span class="additional-info">${showing.additional_info}</span>`
                                                              : ""
                                                          }
                                                          <p>${
                                                            showing.time_start
                                                          } - ${
                                                        showing.time_end
                                                      }</p>
                                                          <a href="${
                                                            showing.ticket_url
                                                          }" class="btn btn-primary btn-sm" target="_blank">Koop Tickets</a>
                                                          <a href="${
                                                            showing.information_url
                                                          }" class="btn btn-secondary btn-sm" target="_blank">Meer Informatie</a>
                                                      </div>
                                                  `
                                                    )
                                                    .join("")}
                                              </div>
                                          `
                                            )
                                            .join("")}
                                      </div>
                                  </li>
                              `
                                )
                                .join("")}
                          </ul>
                      </div>
                  `
        : film.showings[0].screening_info
        ? `
                          <div class="card-collapse screening-info">
                              <p>${film.showings[0].screening_info}</p>
                          </div>
                      `
        : `
                          <div class="card-collapse screening-info">
                              <p>Geen vertoningen beschikbaar.</p>
                          </div>
                      `;

      card.innerHTML = `
                  <div class="card">
                      <a href="${film.url}" target="_blank">
                          <img src="${film.img_url}" class="card-img-top">
                      </a>
                      <div class="card-body">
                          <h2 class="card-title">${film.title}</h2>
                          <div class="film-links">
                              <a href="${
                                film.url
                              }" class="btn btn-primary btn-sm" target="_blank">Cineville</a>
                              <a href="${
                                film.lb_url
                              }" class="btn btn-primary btn-sm" target="_blank">Letterboxd</a>
                              ${
                                film.imdb_id
                                  ? `<a href="https://www.imdb.com/title/${film.imdb_id}" class="btn btn-primary btn-sm" target="_blank">IMDb</a>`
                                  : ""
                              }
                              <a href="https://www.themoviedb.org/movie/${
                                film.tmdb_id
                              }" class="btn btn-primary btn-sm" target="_blank">TMDB</a>
                          </div>
                          <p class="card-text">${film.oneliner}</p>
                      </div>
                      ${showingsOrInfo}
                  </div>
              `;
      filmCards.appendChild(card);
    });
  } else if (sortingMode === "date") {
    const showingsByDate = document.getElementById("DateCard");
    // Group showings by date
    const groupedShowings = {};
    data.forEach((film) => {
      film.showings.forEach((showing) => {
        const date = showing.date;
        if (!groupedShowings[date]) {
          groupedShowings[date] = [];
        }
        groupedShowings[date].push({ film, showing });
      });
    });

    // Sort grouped showings by date and time
    const sortedDates = Object.keys(groupedShowings).sort();

    sortedDates.forEach((date) => {
      const showings = groupedShowings[date];
      showings.sort((a, b) =>
        a.showing.time_start.localeCompare(b.showing.time_start)
      );

      const card = document.createElement("div");
      card.className = "col-md-4";

      const showingsList = showings
        .map(
          ({ film, showing }) => `
                  <div class="showing">
                      <div class="showing-item">
                          <p><strong><a href="${film.url}" target="_blank">${
            film.title
          }</a></strong><br>
                          ${
                            showing.additional_info
                              ? `<span class="additional-info">${showing.additional_info}</span>`
                              : ""
                          }</p>
                          <p>${showing.location_name}<br>
                          ${showing.time_start} - ${showing.time_end}</p>
                          <a href="${
                            showing.ticket_url
                          }" class="btn btn-primary btn-sm" target="_blank">Koop Tickets</a>
                          <a href="${
                            showing.information_url
                          }" class="btn btn-secondary btn-sm" target="_blank">Meer Informatie</a>
                      </div>
                  </div>
              `
        )
        .join("");

      const showingCount = showings.length;

      card.innerHTML = `
                  <div class="card">
                      <div class="card-body">
                          <h2 class="card-title">${formatDateToDutch(
                            date
                          )}</h2>                                    
                          <button class="btn btn-link" data-bs-toggle="collapse" data-bs-target="#showingsList-${date}">
                              Toon ${showingCount} ${
        showingCount === 1 ? "Voorstelling" : "Voorstellingen"
      }
                          </button>
                          <div class="collapse" id="showingsList-${date}">
                              ${showingsList}
                          </div>
                      </div>
                  </div>
              `;

      showingsByDate.appendChild(card);
    });
  }
}

/// Render page

//
fetchDataAndRender(sortingMode);

//
selectCity();
