(function() {
  var table, details_table;

  window.submit_choose_cols = function() {
    var boxes = $("#column-selector .dropdown-item:not(.control)");
    var result = [];
    boxes.each(function() {
      if ($(this).hasClass("selected")) {
        result.push($(this).attr("data-name"));
      }
    });
    $.cookie("pcr_choosecols", result.join(), {
      path: '/'
    });
    return set_cols(result);
  };

  window.set_cols = function(cols) {
      table.columns().visible(false);
      table.columns(0).visible(true);
      if (details_table) {
        details_table.columns().visible(false);
        details_table.columns(1).visible(true);
      }
      var num_cols = [];
      var text_cols = [];
      for (var i = 0; i < cols.length; i++) {
        if (cols[i] === "") {
            continue;
        }
        if (isNaN(cols[i])) {
          text_cols.push(cols[i]);
        }
        else {
          num_cols.push(cols[i]);
        }
      }
      table.columns().every(function() {
        var headerClass = $.grep(this.header().className.split(" "), function(v, i) {
          return v.indexOf("col_") === 0;
        }).join().substr(4);
        if (text_cols.indexOf(headerClass) !== -1) {
          num_cols.push(this.index());
        }
      });
      table.columns(num_cols).visible(true);

      // check whether to fit columns or introduce scrollbars
      table.settings()[0].oFeatures.bAutoWidth = true;
      table.columns.adjust().draw();
      var lotsOfColumns = $("#course-table").width() > $("#course-table").closest(".dataTables_scrollBody").width();

      // do appropriate resizing
      $("#course-table_wrapper .dataTable, #course-table_wrapper .dataTables_scrollHeadInner").css({"width": ""});
      table.settings()[0].oFeatures.bAutoWidth = lotsOfColumns;
      if (!lotsOfColumns) {
        table.settings()[0].aoColumns = table.settings()[0].aoColumns.map(function(x) {
            x.sWidth = undefined;
            return x;
        });
      }
      table.columns.adjust().draw();

      if (details_table) {
        var num_cols = [];
        details_table.columns().every(function() {
          var headerClass = $.grep(this.header().className.split(" "), function(v, i) {
            return v.indexOf("col_") === 0;
          }).join().substr(4);
          if (text_cols.indexOf(headerClass) !== -1 || text_cols == "responses") {
            num_cols.push(this.index());
          }
        });
        details_table.columns(num_cols).visible(true);

        // check whether to fit columns or introduce scrollbars
        details_table.settings()[0].oFeatures.bAutoWidth = true;
        details_table.columns.adjust().draw();
        lotsOfColumns = $("#course-details-table").width() > $("#course-details-table").closest(".dataTables_scrollBody").width();

        // do appropriate resizing
        $("#course-details-table_wrapper .dataTable, #course-details-table_wrapper .dataTables_scrollHeadInner").css({"width": ""});
        details_table.settings()[0].oFeatures.bAutoWidth = lotsOfColumns;
        if (!lotsOfColumns) {
          details_table.settings()[0].aoColumns = details_table.settings()[0].aoColumns.map(function(x) {
              x.sWidth = undefined;
              return x;
          });
        }
        details_table.columns.adjust().draw();
      }
  };

  window.set_viewmode = function(view_id) {
    if (("" + view_id) === "0") {
      $("#view_average").addClass("btn-primary").removeClass("btn-secondary");
      $("#view_recent").addClass("btn-secondary").removeClass("btn-primary");
      $(".cell_average").show();
      $(".cell_recent").hide();
    } else {
      $("#view_recent").addClass("btn-primary").removeClass("btn-secondary");
      $("#view_average").addClass("btn-secondary").removeClass("btn-primary");
      $(".cell_average").hide();
      $(".cell_recent").show();
    }
    $.cookie("pcr_viewmode", view_id, {
      path: '/'
    });
    return $('#course-table').trigger('update');
  };

  $(document).ready(function() {
    $('.sec_row_hidden').hide();

    if ($.cookie("pcr_viewmode") == null) {
      $.cookie("pcr_viewmode", "0", {
        path: '/'
      });
    }

    table = $("#course-table").removeClass("d-none").DataTable({
        select: {"department": {"style": "multi"}, "course": {"style": "single"}, "instructor": false}[$("#banner-info").attr("data-type")],
        columnDefs: [
            {
                targets: "col_section",
                visible: false
            }
        ],
        autoWidth: false,
        paging: false,
        scrollX: true,
        scrollY: $("#banner-info").attr("data-type") == "department" ? 450 : 300,
        scrollCollapse: true,
        dom: '<"toolbar">frtip',
        language: {
            search: "",
            paginate: {
                previous: "<i class='fa fa-chevron-left'></i>",
                next: "<i class='fa fa-chevron-right'></i>"
            }
        },
        drawCallback: function() {
            set_viewmode($.cookie("pcr_viewmode"));
        }
    });

    $("#chart-clear").click(function(e) {
        e.preventDefault();
        table.rows().deselect();
    });

    table.on("select deselect", function(e) {
        if ($("#banner-info").attr("data-type") == "department") {
            var num_selected = table.rows({selected: true}).count();
            if (num_selected >= 5) {
                table.rows(Array.prototype.slice.call(table.rows({selected: true}).indexes()).slice(4)).deselect();
            }
            if (num_selected >= 2) {
                $("#row-select-placeholder").hide();
                $("#row-select-chart-container").show();
                d3.select("svg").selectAll("*").remove();
                var n = 3; // The number of series.
                m = num_selected; // The number of values per series.
                keys = ['Course Quality', 'Instructor Quality', 'Difficulty']
                tickLabels = Array.prototype.slice.call(table.rows({selected: true}).data().map(function(x) {
                            return $(x[0]).text();
                        })).slice(0, 4)

                // The xz array has m elements, representing the x-values shared by all series.
                // The yz array has n elements, representing the y-values of each of the n series.
                // Each yz[i] is an array of m non-negative numbers representing a y-value for xz[i].
                // The y01z array has the same structure as yz, but with stacked [y₀, y₁] instead of y.

                var data = [];
                values = [];
                table.columns(":visible").every(function(col) {
                    var header = $(this.header());
                    if (header.hasClass("col_name") || header.hasClass("col_code")) {
                        return;
                    }
                    data.push({
                        label: $.trim(header.text()),
                        data: Array.from(table.rows({selected: true}).data().map(function(x) {
                            if (!x[col]) {
                                return 0;
                            }
                            return parseFloat($(x[col])[0].innerHTML);
                        })),
                    });
                    values.push(Array.from(table.rows({selected: true}).data().map(function(x) {
                        if (!x[col]) {
                            return 0;
                        }
                        return parseFloat($(x[col])[0].innerHTML);
                    })))
                });

                var xz = d3.range(m),
                yz = values,
                y01z = d3.stack().keys(d3.range(n))(d3.transpose(yz)),
                yMax = d3.max(yz, function(y) { return d3.max(y); }),
                y1Max = d3.max(y01z, function(y) { return d3.max(y, function(d) { return d[1]; }); });

                var svg = d3.select("svg"),
                margin = {top: 60, right: 10, bottom: 20, left: 30},
                width = +svg.attr("width") - margin.left - margin.right,
                height = +svg.attr("height") - margin.top - margin.bottom,
                g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

                // var tip = d3.tip()
                //   .attr('class', 'd3-tip')
                //   .html(
                //     "<strong>Frequency:</strong> <span style='color:red'>" + "Hello" + "</span>"
                //   );
                //
                // g.call(tip);

                var x = d3.scaleBand()
                .domain(xz)
                .rangeRound([0, width])
                .padding(0.08);

                var y = d3.scaleLinear()
                .domain([0, y1Max])
                .range([height, 0]);

                // var color = d3.scaleOrdinal()
                //     .domain(d3.range(n))
                //     .range(d3.schemeCategory20c);

                var color = d3.scaleOrdinal().range(["#6274f1", "#ffc107", "#76bf96"]);

                var series = g.selectAll(".series")
                .data(y01z)
                .enter().append("g")
                .attr("fill", function(d, i) { return color(i); });

                var rect = series.selectAll("rect")
                .data(function(d) { return d; })
                .enter().append("rect")
                .attr("class", "bar")
                .attr("x", function(d, i) { return x(i); })
                .attr("y", height)
                .attr("width", x.bandwidth())
                .attr("height", 0)
                .on("mouseover", function(d) {
                  console.log(d);
                })
                .on("mouseout", function(d) {
                  console.log('out');
                });

                rect.transition()
                .delay(function(d, i) { return i * 10; })
                .attr("y", function(d) { return y(d[1]); })
                .attr("height", function(d) { return y(d[0]) - y(d[1]); });

                g.append("g")
                .attr("class", "axis axis--x")
                .attr("transform", "translate(0," + height + ")")
                .attr("font-weight", "bold")
                .call(d3.axisBottom(x)
                .tickPadding(2)
                .tickFormat(function(d, i){ return tickLabels[i]}));

                g.append("g")
                .attr("class", "axis axis--y")
                .call(d3.axisLeft(y).ticks(null, "s"))
                .append("text")
                .attr("transform", "rotate(-90)")
                .attr("x", 2)
                // .attr("y", y(y.ticks().pop()) + 0.5)
                // .attr("dy", "0.32em")
                .attr("fill", "#000")
                .attr("font-weight", "bold")
                .attr("y", 6)
                .attr("dy", ".71em")
                .style("text-anchor", "end")
                .text("Rating");

                var legend = g.append("g")
                .attr("font-family", "sans-serif")
                .attr("font-size", 10)
                .attr("text-anchor", "end")
                .selectAll("g")
                .data(keys.slice())
                .enter().append("g")
                .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

                legend.append("rect")
                .attr("x", width - 19)
                .attr("width", 19)
                .attr("height", 19)
                .attr("fill", color);

                legend.append("text")
                .attr("x", width - 24)
                .attr("y", 9.5)
                .attr("dy", "0.32em")
                .text(function(d) { return d; });

                d3.selectAll("input")
                .on("change", changed);

                // var timeout = d3.timeout(function() {
                //   d3.select("input[value=\"grouped\"]")
                //       .property("checked", true)
                //       .dispatch("change");
                // }, 2000);

                function changed() {
                  if (this.value === "grouped") {
                    transitionGrouped();
                  }
                  else  {
                    transitionStacked();
                  }
                  svg.selectAll("g.axis--y").remove()
                  g.append("g")
                  .attr("class", "axis axis--y")
                  .call(d3.axisLeft(y).ticks(null, "s"))
                  .append("text")
                  .attr("transform", "rotate(-90)")
                  .attr("x", 2)
                  .attr("y", 6)
                  .attr("dy", ".71em")
                  .attr("fill", "#000")
                  .attr("font-weight", "bold")
                  .attr("text-anchor", "end")
                  .text("Rating");
                }

                function transitionGrouped() {
                  y.domain([0, yMax]);

                  rect.transition()
                  .duration(500)
                  .delay(function(d, i) { return i * 10; })
                  .attr("x", function(d, i) { return x(i) + x.bandwidth() / n * this.parentNode.__data__.key; })
                  .attr("width", x.bandwidth() / n)
                  .transition()
                  .attr("y", function(d) { return y(d[1] - d[0]); })
                  .attr("height", function(d) { return y(0) - y(d[1] - d[0]); });
                }

                function transitionStacked() {
                  y.domain([0, y1Max]);

                  rect.transition()
                  .duration(500)
                  .delay(function(d, i) { return i * 10; })
                  .attr("y", function(d) { return y(d[1]); })
                  .attr("height", function(d) { return y(d[0]) - y(d[1]); })
                  .transition()
                  .attr("x", function(d, i) { return x(i); })
                  .attr("width", x.bandwidth());
                }

                // var data = [];
                // var colors = ["#6274f1", "#ffc107", "#76bf96", "#df5d56"];
                // table.columns(":visible").every(function(col) {
                //     var header = $(this.header());
                //     if (header.hasClass("col_name") || header.hasClass("col_code")) {
                //         return;
                //     }
                //     data.push({
                //         label: $.trim(header.text()),
                //         data: Array.from(table.rows({selected: true}).data().map(function(x) {
                //             if (!x[col]) {
                //                 return 0;
                //             }
                //             return parseFloat($(x[col])[0].innerHTML);
                //         })),
                //         backgroundColor: colors[col % colors.length]
                //     });
                // });
                // new Chart("row-select-chart", {
                //     type: "bar",
                //     responsive: true,
                //     maintainAspectRatio: false,
                //     data: {
                //         labels: Array.prototype.slice.call(table.rows({selected: true}).data().map(function(x) {
                //             return $(x[0]).text();
                //         })).slice(0, 4),
                //         datasets: data.slice(0, 4).map(function(item) {
                //             item.data = item.data.slice(0, 4);
                //             return item;
                //         })
                //     },
                //     options: {
                //         legend: {
                //             labels: {
                //                 fontFamily: "Lato",
                //                 fontSize: 10,
                //                 boxWidth: 10
                //             }
                //         },
                //         events: [],
                //         scales: {
                //         xAxes: [{
                //                 ticks: {
                //                     autoSkip: false,
                //                     maxRotation: 0,
                //                     minRotation: 0,
                //                     fontSize: 9
                //                 }
                //             }],
                //             yAxes: [{
                //                 display: true,
                //                 ticks: {
                //                     beginAtZero: true,
                //                     stepSize: 1,
                //                     max: 4
                //                 }
                //             }]
                //         }
                //     }
                // });
            }
            else {
                $("#row-select-placeholder").show();
                $("#row-select-chart-container").hide();
            }
        }
    });

    var courseTableBody = $("#course-table").closest(".dataTables_scrollBody");
    if (courseTableBody[0].scrollHeight > courseTableBody.height()) {
        $("#scroll-indicator").show();
        courseTableBody.on("scroll", function() {
            if (courseTableBody[0].scrollTop > 0) {
                $("#scroll-indicator").slideUp();
            }
        });
    }

    $("#course-table tbody").on("click", "tr", function(e) {
        if ($("#course-details").length) {
            var data = table.row(this).data();
            var details = data[data.length - 1];
            $("#select-prof").hide();
            $("#course-details-wrapper").show().find("h3").text($.trim($("<div>" + data[0] + "</div>").text()));
            $("#course-details-data").html(details);
            var details_table_element = $("#course-details-data").find("table").attr("id", "course-details-table");
            $("#course-details-comments .comments").children().remove();
            details_table_element.find(".sec_row_hidden p").appendTo("#course-details-comments .comments");
            var comment_list = $("#course-details-comments .list")
            comment_list.children().remove();
            $("#course-details-comments .comments p").each(function() {
                $(this).find("br").remove();
                var sem = $("<div />").text($(this).attr("data-semester"));
                sem.click(function(e) {
                    $("#course-details-comments .list div").removeClass("selected");
                    $("#course-details-comments .comments p").hide();
                    $(this).addClass("selected");
                    $("#course-details-comments .comments p[data-semester='" + $(this).text() + "']").show();
                    e.preventDefault();
                });
                comment_list.append(sem);
            });
            $("#course-details-comments .empty").toggle(!comment_list.children().length);
            $("#course-details-comments .list div:first-child").click();
            details_table_element.find(".sec_row_hidden").remove();
            var details_dt = details_table_element.DataTable({
                columnDefs: [
                    {
                        targets: "col_icon",
                        visible: false
                    },
                    {
                        targets: "col_name",
                        title: "Class"
                    }
                ],
                autoWidth: false,
                paging: false,
                scrollX: true,
                scrollCollapse: true,
                dom: '<"toolbar">frtip',
                language: {
                    search: "",
                    paginate: {
                        previous: "<i class='fa fa-chevron-left'></i>",
                        next: "<i class='fa fa-chevron-right'></i>"
                    }
                },
                order: [[1, "desc"]]
            });

            $("#course-details-data").find("input[type=search]").addClass("form-control form-control-sm");
            $("#view_ratings, #view_comments").click(function(e) {
                e.preventDefault();
                var is_ratings = $(this).attr("id") == "view_ratings";
                $("#view_ratings").toggleClass("btn-sub-primary", is_ratings).toggleClass("btn-sub-secondary", !is_ratings);
                $("#view_comments").toggleClass("btn-sub-primary", !is_ratings).toggleClass("btn-sub-secondary", is_ratings);
                $("#course-details-data, #course-details-dropdown").toggle(is_ratings);
                $("#course-details-comments").toggle(!is_ratings);
                if (is_ratings) {
                    window.submit_choose_cols();
                }
            });

            details_table = details_dt;
            const cols_saved = $.cookie("pcr_choosecols");
            if (cols_saved !== null) {
                set_cols(cols_saved.split(","));
            }
            else {
                set_cols(["rCourseQuality", "rInstructorQuality", "rDifficulty", "rAmountLearned"]);
            }
        }
    });

    $("#course-table_filter input[type=search]").addClass("form-control form-control-sm");
    table.columns().visible(false);
    table.columns([0, 1, 2, 3, 4]).visible(true);

    $("#course-table_wrapper div.toolbar").append("<div class='btn-group mr-1'><button id='view_average' class='btn btn-sm btn-primary'>Average</button> <button id='view_recent' class='btn btn-secondary btn-sm'>Most Recent</button></div>");

    $("#view_average").click(function(e) {
      e.preventDefault();
      window.set_viewmode(0);
    });

    $("#view_recent").click(function(e) {
      e.preventDefault();
      window.set_viewmode(1);
    });

    set_viewmode($.cookie("pcr_viewmode"));
    const cols_saved = $.cookie("pcr_choosecols");
    if (cols_saved !== null) {
      set_cols(cols_saved.split(","));
    }

    // create a div element for the button
    var btn_div = document.createElement("div");
    btn_div.setAttribute("class", "btn-group dropleft");
    $("#course-table_filter").prepend( btn_div );
    $("#course-table_wrapper div.toolbar").append("<button id='course-dropdown' class='btn btn-primary btn-sm dropdown-toggle ml-2' data-toggle='dropdown'><i class='fa fa-plus'></i></button>");
    // create a div element for the drop down menu
    var div = $("<div id='column-selector' class='column-selector dropdown-menu' aria-labelledby='course-dropdown' />");
    div.append("<a class='dropdown-item control' data-id='select-all' data-name='select-all'>Select all</a><a class='dropdown-item control' data-id='clear' data-name='clear'>Clear</a><hr />");
    // create dropdown menu inside div
    table.columns().every(function() {
        var title = $(this.header()).text().trim();
        var item = $("<a class='dropdown-item' data-id='" + this.index() + "'>" + title + "</a>");
        item.attr("data-name", $.grep(this.header().className.split(" "), function(v, i) {
          return v.indexOf('col_') === 0;
        }).join().substr(4));
        if (title == "Instructor" || title == "Section") {
            return;
        }
        div.append(item);
        if (this.visible()) {
            item.addClass("selected");
        }
    });
    $("#course-table_wrapper div.toolbar").prepend(div);

    div.clone().attr("id", "details-column-selector").insertAfter("#course-details-dropdown");
    $("#course-details-dropdown").addClass("dropdown-toggle").attr("data-toggle", "dropdown");

    $('#column-selector .dropdown-item').click(function(e) {
        e.stopPropagation();
        var col_id = $(this).attr("data-id");
        if (col_id == "select-all") {
            $("#column-selector .dropdown-item:not(.control), #details-column-selector .dropdown-item:not(.control)").addClass("selected");
        }
        else if (col_id == "clear") {
            $("#column-selector .dropdown-item:not(.control), #details-column-selector .dropdown-item:not(.control)").removeClass("selected");
        }
        else {
            $(this).toggleClass("selected");
            $("#details-column-selector .dropdown-item[data-name='" + $(this).attr("data-name") + "']").toggleClass("selected");
        }
        window.submit_choose_cols();
    });

    $("#details-column-selector .dropdown-item").click(function(e) {
        e.stopPropagation();
        $('#column-selector .dropdown-item[data-name="' + $(this).attr("data-name") + '"]').click();
    });
  });

}).call(this);
