"""This program uses matplotlib to generate an interactive corsi blocks game.
We use a class to implement the game because we need to carry around a bunch of metadata that things like onlick
need to access.

The display of the corsi blocks occurs within a single method run_corsi which reads in the current difficulty level and then generates a sequence of blocks which it then proceeds to display. At the end of the display it sets up a simple sequence counter that points to which corsi block we are at (the 1st one) and waits for mouse presses on the main screen. Pressing any of the menu items aborts the trial just displayed and executes the menu item. Clicking on the main screen tests to see if the click is on an appropriate block. If it is not, feedback is given and the next trial is started. If the block is appropriate then we move the counter along until all blocks are done, at which point we give feed back and start the next trial.

To generate app on mac

python ~/bin/pyinstaller-2.0/pyinstaller.py -F -w -y corsiblocks.py

TODO: Implement staircase method and give realtime feedback at bottom as a strip chart and current threshold value
"""
import matplotlib
matplotlib.use('macosx')
import pylab, time

class CorsiBlocks:
  def __init__(self):
    self.setup_main_screen()
    self.span = 2 #How many block
    self.running = False
    self.streak = 0
    self.staircase_streak = 2 #How many corrects before we increase difficulty
    self.span_history = [] #Our trial results

  def setup_main_screen(self):
    self.fig = pylab.figure(figsize=(6,8))
    pylab.subplots_adjust(top=.95, bottom=0.05, left=.05, right=.95, hspace=.15, wspace=.15)
    pylab.suptitle('Corsi Blocks')

    rows = 10
    cols = 8

    self.ax = {}
    #Main corsi blocks display
    self.ax['main'] = pylab.subplot2grid((rows, cols), (0, 0), colspan=cols, rowspan=rows-1)
    self.clear_main_screen('Click anywhere to start')

    #The staircase display with span estimate
    self.ax['staircase'] = pylab.subplot2grid((rows, cols), (9, 1), colspan=cols-1)
    pylab.setp(self.ax['staircase'], 'xticks', [], 'yticks', [])
    self.cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)

  def clear_main_screen(self, msg=None):
    ax = self.ax['main']
    ax.cla()
    pylab.setp(ax,'xlim', [-1, 5], 'ylim', [-1, 5], 'xticks', [], 'yticks', [])
    if msg is not None:
      ax.text(2,2,msg,horizontalalignment='center')

  def start_session(self):
    self.running = True
    bc = self.span
    idx = pylab.arange(5*5) #we work on a 5,5 square
    pylab.shuffle(idx)
    self.this_sequence = idx[:bc] #Sequence of blocks
    self.clear_main_screen()
    ax = self.ax['main']
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
    if result:
      msg = 'Correct!\nClick anywhere to continue'
      self.streak += 1
      self.span_history.append(self.span)
      if self.streak >= self.staircase_streak:
        self.span += 1
        self.streak = 0
    else:
      msg = 'Wrong :(\nClick anywhere to continue'
      self.streak = 0
      self.span = max(1, self.span - 1)

    self.clear_main_screen(msg)
    self.plot_span_history()
    self.running = False
    pylab.draw()

  def plot_span_history(self):
    sh = self.span_history
    l = max(-10, -len(sh))
    my_span = sum(sh[l:])/float(-l)
    ax = self.ax['staircase']
    ax.cla()
    ax.plot(sh,'k.')
    ax.plot([0, len(sh)-1], [my_span, my_span], 'k:')
    pylab.xlabel('Trials')
    pylab.ylabel('Span')
    pylab.setp(ax, 'xlim', [-.5, 1.1*(len(sh)-1)], 'ylim', [0, max(sh)+.5], 'xticks', [len(sh)-1], 'yticks', [my_span], 'yticklabels',['{:1.1f}'.format(my_span)], 'xticklabels', [len(sh)])

  def onclick(self, event):
    if event.name == 'button_press_event':
      if event.inaxes == self.ax['main']:#We clicked on main screen
        if self.running: #We are in the middle of a trial
          self.test_block(event)
        else: #We want to start a new trial
          self.start_session()

cb = CorsiBlocks()
pylab.show()