"""This program uses matplotlib to generate an interactive corsi blocks game.
We use a class to implement the game because we need to carry around a bunch of metadata that things like onlick
need to access.

The display of the corsi blocks occurs within a single method run_corsi which reads in the current difficulty level and then generates a sequence of blocks which it then proceeds to display. At the end of the display it sets up a simple sequence counter that points to which corsi block we are at (the 1st one) and waits for mouse presses on the main screen. Pressing any of the menu items aborts the trial just displayed and executes the menu item. Clicking on the main screen tests to see if the click is on an appropriate block. If it is not, feedback is given and the next trial is started. If the block is appropriate then we move the counter along until all blocks are done, at which point we give feed back and start the next trial.

To generate app on mac

python ~/bin/pyinstaller-2.0/pyinstaller.py -F -w -y corsiblocks.py
"""
import matplotlib
matplotlib.use('macosx')
import pylab, time

class CorsiBlocks:
  def __init__(self):
    self.setup_main_screen()
    self.difficulty = 0 #0,1,2
    self.running = False
    self.timer = None

  def setup_main_screen(self):
    self.fig = pylab.figure(figsize=(6,8))
    pylab.subplots_adjust(top=.95, bottom=0.05, left=.05, right=.95, hspace=.15, wspace=.15)
    pylab.suptitle('Corsi Blocks')

    rows = 10
    cols = 4

    self.ax = {}
    #Main corsi blocks display
    self.ax['main'] = pylab.subplot2grid((rows, cols), (0, 0), colspan=4, rowspan=9)
    pylab.setp(self.ax['main'], 'xticks', [], 'yticks', [])

    #Menu
    for n, menu_item in enumerate(['go', 'easy', 'moderate', 'hard']):
      self.ax[menu_item] = pylab.subplot2grid((rows, cols), (9, n))
      h = pylab.text(0.2, 0.5, menu_item)
      pylab.setp(self.ax[menu_item], 'xticks', [], 'yticks', [])
      if menu_item == 'go':
        self.start_button_text = h

    pylab.show()
    self.cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)

  def start_session(self):
    self.running = True
    if self.timer is not None:
      self.timer.stop()
      self.timer.remove_callback(self.start_session)
    self.start_button_text.set_text('Done') #Change start button to indicate new role
    block_count_list = [2,4,8]
    bc = block_count_list[self.difficulty]
    idx = pylab.arange(5*5) #we work on a 5,5 square
    pylab.shuffle(idx)
    self.this_sequence = idx[:bc] #Sequence of blocks
    ax = self.ax['main']
    ax.cla()
    pylab.setp(ax,'xlim', [-1, 5], 'ylim', [-1, 5], 'xticks', [], 'yticks', [])
    self.block_h = []
    for b in xrange(bc):
      x = idx[b]%5
      y = idx[b]/5
      h = ax.plot(x,y,'ks',ms=25)
      self.block_h.append(h)
      pylab.draw()
      time.sleep(1)
    self.current_block = 0

  def test_block(self, event):
    x = event.xdata
    y = event.ydata
    idx = self.this_sequence
    cx = idx[self.current_block]%5
    cy = idx[self.current_block]/5
    if ((x-cx)**2 < .25) and ((y-cy)**2 < .25):
      self.block_h[self.current_block][0].set_markerfacecolor('b')
      pylab.draw()
      self.current_block += 1
      if self.current_block == idx.size:
        self.trial_correct(True)
    else:
      self.trial_correct(False)

  def trial_correct(self, result):
    ax = self.ax['main']
    ax.cla()
    pylab.setp(ax,'xlim', [-1, 5], 'ylim', [-1, 5], 'xticks', [], 'yticks', [])
    if result:
      ax.text(2.5,2.5, 'Correct!')
    else:
      ax.text(2.5,2.5, 'In correct :(')

    self.timer = self.fig.canvas.new_timer(interval=5000)
    self.timer.add_callback(self.start_session)
    self.timer.start()

  def abort_trial(self):
    #Code to close out trial
    self.running = False
    self.start_button_text.set_text('Go') #Change start button to indicate new role

  def set_difficulty(self, level):
    self.difficulty = level
    items = ['easy', 'moderate', 'hard']
    for item in items:
      self.ax[item].patch.set_facecolor('white')
    self.ax[items[level]].patch.set_facecolor('green')

  def onclick(self, event):
    if event.name == 'button_press_event':
      for axname, axval in self.ax.items():
        if event.inaxes == axval:
          if axname == 'main': #We clicked on main screen, trying for a corsi blocks thingy
            self.test_block(event)
          elif axname == 'go':
            if self.running == False:
              self.start_session()
          elif axname == 'easy':
            #Abort this trial
            self.abort_trial()
            self.set_difficulty(0)
          elif axname == 'moderate':
            self.abort_trial()
            self.set_difficulty(1)
          elif axname == 'hard':
            self.abort_trial()
            self.set_difficulty(2)

pylab.ion() #Stupid macosx backend
cb = CorsiBlocks()