import libtorrent
import time
import tempfile
import binascii
import sys


def magnet2torrent(link, torrent_file):
  sess = libtorrent.session()

  params = {
            "save_path": tempfile.gettempdir(),
            "storage_mode":libtorrent.storage_mode_t.storage_mode_sparse,
            "paused": True,
            "auto_managed": True,
            "duplicate_is_error": True
           }
  handle = libtorrent.add_magnet_uri(sess, link, params)
  print "Loading magnet file"
  while True:
    s = handle.status()
    print "waiting..."
    if s.state != 2:
      t = handle.get_torrent_info()
      print "Saving torrent -=%s=-" % t.name()
      fs = libtorrent.file_storage()
      for i in t.files():
        fs.add_file(i)
        print "\tFile: %s" % i.path
      ct = libtorrent.create_torrent(fs) 
      for i in t.trackers():
        print "\tTracker: %s, %s " % (i.url, i.tier)
        ct.add_tracker(i.url, i.tier)
      ct.set_creator(t.creator())
      ct.set_comment(t.comment())
      ct.set_priv(t.priv())
      f = open(torrent_file, "wb")
      g = ct.generate()
      g["info"]["pieces"] = "".join([binascii.unhexlify("%s" % t.hash_for_piece(i)) for i in range(t.num_pieces())])
      g["info"]["piece length"] = t.piece_length()
      g["info"]["length"] = t.total_size()
      f.write(libtorrent.bencode(g))
      f.close()
      return
    time.sleep(1) # sleep for a second

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print """
Usage:
  magnet2torrent.py "magnet:?..."  [output file]
"""
    sys.exit()
  link = sys.argv[1]
  file_name = "torrent.torrent"
  if len(sys.argv) >= 3:
    file_name = sys.argv[2]
  magnet2torrent(link, file_name)
