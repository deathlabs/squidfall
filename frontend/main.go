package main

import (
	"embed"
	"fmt"
	"io/fs"
	"net/http"
	"os"
	"strings"
)

//go:embed all:out
var files embed.FS

func main() {
	var (
		err          error
		fileServer   http.Handler
		indexHandler func(http.ResponseWriter, *http.Request)
		site         fs.FS
	)

	site, err = fs.Sub(files, "out")
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}

	fileServer = http.FileServer(http.FS(site))

	indexHandler = func(w http.ResponseWriter, r *http.Request) {
		var (
			path    string
			statErr error
		)

		path = strings.TrimPrefix(r.URL.Path, "/")

		if path != "" && !strings.HasSuffix(path, "/") {
			_, statErr = fs.Stat(site, path)
			if statErr != nil {
				_, statErr = fs.Stat(site, path+".html")
				if statErr == nil {
					r.URL.Path += ".html"
				}
			}
		}

		fileServer.ServeHTTP(w, r)
	}

	http.HandleFunc("/", indexHandler)

	err = http.ListenAndServe(":8080", nil)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
