package main

import (
	"fmt"
	"github.com/rjeczalik/notify"
	"log"
	"net/http"
	"os"
	"path"
	"strings"
	"time"
)

func main() {
	var watcher Watcher
	watcher.init()
}

type Watcher struct {
	home          string
	trackedFolder string
	pdfDst        string
	imgDst string
}

func (w *Watcher) init() {
	w.home = os.Getenv("HOME")
	w.imgDst = path.Join(w.home, "Pictures")
	w.pdfDst = path.Join(w.home, "Documents")
	w.trackedFolder = path.Join(w.home, "Downloads")
	w.config()
}

func (w Watcher) config() {
	file, _ := os.OpenFile(".handling.log", os.O_RDWR|os.O_CREATE|os.O_APPEND, 0666)
	defer file.Close()
	log.SetOutput(file)
	c := make(chan notify.EventInfo, 1)
	err := notify.Watch(w.trackedFolder, c, notify.InMovedTo)
	if err != nil {
		log.Println("ERROR:", err)
	}
	defer notify.Stop(c)
	for {
		change := <- c
		switch change.Event() {
		case notify.InMovedTo:
			if !strings.HasSuffix(change.Path(), ".part") {
				file, _ := os.Open(change.Path())
				filetype, _ := GetFileContentType(file)
				if strings.HasSuffix(change.Path(), ".pdf") {
					move(change.Path(), w.pdfDst)
				} else if strings.HasPrefix(filetype, "image") {
					move(change.Path(), w.imgDst)
				}
			}
		}

	}
}

func move(srcPath string, dstPath string) {
	basename := path.Base(srcPath)
	newPath := path.Join(dstPath, basename)
	err := os.Rename(srcPath, newPath)
	if err != nil {
		log.Println("-", err)
	} else {
		log.Println("- Succesfully moved", basename, "at", fmt.Sprint(time.Now().Clock()), "of", fmt.Sprint(time.Now().Date()))
	}
}

func GetFileContentType(out *os.File) (string, error) {
	buffer := make([]byte, 512)
	_, err := out.Read(buffer)
	if err != nil {
		log.Fatalln(err)
	}
	contentType := http.DetectContentType(buffer)
	contentType = strings.Split(contentType, "/")[0]
	return contentType, nil
}
