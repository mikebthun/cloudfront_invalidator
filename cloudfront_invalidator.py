#!/usr/bin/python

import boto
 
import os
 
import sys,getopt
 
import logging

logger = logging.getLogger('stencil')
hdlr = logging.StreamHandler(sys.stdout)
#hdlr = logging.FileHandler('stencil.log') 
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO) #logging.DEBUG
import commands
 
def help():
  print "cloudfront_invalidator.py"
  print "\t--distribution YOUR_CLOUD_FRONT_DISTRO"
  print "\t--paths /absolute/cloudfront/path/to/blah.html,/absolute/cloudfront/path/to/blah2.html,"
  print "\t--aws-key [YOUR_AWS_KEY] --aws-secret [YOUR_AWS_SECRET]"
  print "\tif --paths is ommited will check CWD for git repo and grab all files."
  print "\t--path sets prefix for cloudfront absolute path for git files"
 
  sys.exit(2)


def git_to_invalidate_format(path):

  ignores = ['.gitignore', '.kitchen.yml', 'Berksfile']

  cmd = "git ls-files"

  (status,output) = commands.getstatusoutput(cmd)

  if status>0:
    logger.error("Could not run %s: %s\n%s", cmd, output)
    sys.exit(2)

  files = output.split('\n')

  modified_files = ["%s%s" % (path, f.strip()) for f in files if f not in ignores ]


  return ",".join(modified_files)
 

def main(argv):

  distribution=None
  paths=[]
  awsKey = None
  awsSecret = None

  # path to prefix invalidation with
  path="/"
 
  #grab command line argurments
  try:
    opts, args = getopt.getopt(argv,"hi:o:",["distribution=","paths=","prefix-path=","aws-key=","aws-secret="])
  except getopt.GetoptError:
    help()

  for opt, arg in opts:
    if opt == '-h':
      help()
    elif opt in  ("--distribution"):
      distribution = u"%s" % arg
    elif opt in ( "--paths" ):
      paths = arg.split(",")
    elif opt in ( "--prefix-path" ):
      path = arg
    elif opt in ( "--aws-key" ):
      awsKey = arg
    elif opt in ( "--aws-secret" ):
      awsSecret = arg


  if distribution==None:
    print " * Fatal: Missing distribution"
    help()
    sys.exit(2)

  if None in [ awsKey, awsSecret ]:
    print " * Fatal: Missing aws key or secret"
    help()
    sys.exit(2)


  if len(paths)<1:
    # print " * Fatal: No paths?"
    # sys.exit(2)
    paths = git_to_invalidate_format(path).split(",")

  print " * Invalidating: %s %d" % ( paths, len(paths))
 
  try:
    c = boto.connect_cloudfront( awsKey, awsSecret )
  except Exception as e:
    logger.error("Could not connect to boto %s" % e)
    sys.exit(2)
 

  try:
    inval_req = c.create_invalidation_request(distribution, paths)
  except Exception, e:
    print " * FATAL: Could not create invalidation request"
    print e
    sys.exit(2)

  print " * Completed... [OK]"
  

if __name__ == "__main__":
  main(sys.argv[1:])